"""
Migração: Converter orders.id e order_items.order_id de INTEGER para VARCHAR(6)

Execute UMA VEZ, com o servidor parado:
    cd backend
    python alter_db_order_id.py

O que faz:
  - Cria coluna 'id_new' VARCHAR(6) na tabela 'orders'
  - Copia os IDs existentes convertidos para string (ex: 1 -> '1', 12 -> '12')
  - Renomeia colunas (orders.id -> orders.id_old, orders.id_new -> orders.id)
  - Faz o mesmo para order_items.order_id (FK)
  - Reconstrói a FK constraint
  - Remove coluna temporária

Compatibilidade: SQLite (desenvolvimento) e PostgreSQL (produção).
"""

import os
import sys

# Adiciona o diretório raiz ao path para importar config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text

# Detecta a DATABASE_URL do .env
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

DATABASE_URL = (
    os.environ.get('DATABASE_URL') or
    os.environ.get('SQLALCHEMY_DATABASE_URI') or
    os.environ.get('DEV_DATABASE_URI') or
    os.environ.get('PROD_DATABASE_URI')
)

if not DATABASE_URL:
    # Fallback: tenta importar do config.py
    try:
        from config import Config
        DATABASE_URL = Config.SQLALCHEMY_DATABASE_URI
    except Exception:
        print("ERRO: Não foi possível determinar a DATABASE_URL.")
        print("Defina a variável DATABASE_URL no arquivo backend/.env")
        sys.exit(1)

print(f"[MIGRAÇÃO] Conectando em: {DATABASE_URL[:40]}...")
engine = create_engine(DATABASE_URL)


def is_sqlite():
    return 'sqlite' in DATABASE_URL.lower()


def migrate():
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            if is_sqlite():
                _migrate_sqlite(conn)
            else:
                _migrate_postgres(conn)
            trans.commit()
            print("[MIGRAÇÃO] ✅ Concluída com sucesso!")
        except Exception as e:
            trans.rollback()
            print(f"[MIGRAÇÃO] ❌ Erro: {e}")
            raise


def _migrate_sqlite(conn):
    """SQLite não suporta ALTER COLUMN, então precisamos recriar as tabelas."""
    print("[MIGRAÇÃO][SQLite] Iniciando migração das tabelas orders e order_items...")

    # 1. Recriar order_items sem a FK (SQLite não tem DROP CONSTRAINT)
    conn.execute(text("""
        CREATE TABLE order_items_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id VARCHAR(6),
            product_id INTEGER,
            product_variant_id INTEGER,
            quantity INTEGER,
            price NUMERIC(10, 2)
        )
    """))
    conn.execute(text("""
        INSERT INTO order_items_new (id, order_id, product_id, product_variant_id, quantity, price)
        SELECT id, CAST(order_id AS TEXT), product_id, product_variant_id, quantity, price
        FROM order_items
    """))
    conn.execute(text("DROP TABLE order_items"))
    conn.execute(text("ALTER TABLE order_items_new RENAME TO order_items"))
    print("[MIGRAÇÃO][SQLite] Tabela order_items migrada.")

    # 2. Recriar orders com id VARCHAR(6)
    conn.execute(text("""
        CREATE TABLE orders_new (
            id VARCHAR(6) PRIMARY KEY,
            user_id INTEGER,
            total NUMERIC(10, 2),
            coupon_id INTEGER,
            discount_amount NUMERIC(10, 2),
            created_at DATETIME,
            status VARCHAR(50),
            payment_status VARCHAR(50),
            payment_id VARCHAR(100),
            payment_method VARCHAR(50),
            installments INTEGER,
            is_paid BOOLEAN,
            shipping_price NUMERIC(10, 2),
            shipping_service_name VARCHAR(100),
            shipping_service_id INTEGER,
            shipping_delivery_time INTEGER,
            shipping_cep VARCHAR(10),
            shipping_address VARCHAR(255),
            shipping_number VARCHAR(20),
            shipping_complement VARCHAR(100),
            shipping_neighborhood VARCHAR(100),
            shipping_city VARCHAR(100),
            shipping_state VARCHAR(2),
            customer_cpf VARCHAR(14)
        )
    """))
    conn.execute(text("""
        INSERT INTO orders_new
        SELECT
            CAST(id AS TEXT),
            user_id, total, coupon_id, discount_amount, created_at,
            status, payment_status, payment_id, payment_method, installments,
            is_paid, shipping_price, shipping_service_name, shipping_service_id,
            shipping_delivery_time, shipping_cep, shipping_address, shipping_number,
            shipping_complement, shipping_neighborhood, shipping_city, shipping_state,
            customer_cpf
        FROM orders
    """))
    conn.execute(text("DROP TABLE orders"))
    conn.execute(text("ALTER TABLE orders_new RENAME TO orders"))
    print("[MIGRAÇÃO][SQLite] Tabela orders migrada.")


def _migrate_postgres(conn):
    """PostgreSQL suporta ALTER COLUMN com USING."""
    print("[MIGRAÇÃO][PostgreSQL] Iniciando migração...")

    # 1. Remover FK de order_items antes de alterar orders.id
    # (O nome da constraint pode variar — detectamos dinamicamente)
    result = conn.execute(text("""
        SELECT constraint_name
        FROM information_schema.table_constraints
        WHERE table_name = 'order_items'
          AND constraint_type = 'FOREIGN KEY'
          AND constraint_name LIKE '%order_id%'
    """))
    fk_name = result.scalar()
    if fk_name:
        conn.execute(text(f'ALTER TABLE order_items DROP CONSTRAINT "{fk_name}"'))
        print(f"[MIGRAÇÃO][PostgreSQL] FK removida: {fk_name}")

    # 2. Alterar order_items.order_id para VARCHAR(6)
    conn.execute(text(
        "ALTER TABLE order_items ALTER COLUMN order_id TYPE VARCHAR(6) USING order_id::TEXT"
    ))
    print("[MIGRAÇÃO][PostgreSQL] order_items.order_id convertido para VARCHAR(6).")

    # 3. Alterar orders.id para VARCHAR(6)
    conn.execute(text(
        "ALTER TABLE orders ALTER COLUMN id TYPE VARCHAR(6) USING id::TEXT"
    ))
    print("[MIGRAÇÃO][PostgreSQL] orders.id convertido para VARCHAR(6).")

    # 4. Recriar a FK constraint
    conn.execute(text("""
        ALTER TABLE order_items
        ADD CONSTRAINT order_items_order_id_fkey
        FOREIGN KEY (order_id) REFERENCES orders(id)
    """))
    print("[MIGRAÇÃO][PostgreSQL] FK order_items -> orders recriada.")


if __name__ == '__main__':
    print("=" * 60)
    print("  MIGRAÇÃO: Order ID  INTEGER -> VARCHAR(6)")
    print("  Os pedidos existentes terão IDs como '1', '2', etc.")
    print("  Novos pedidos terão formato '4821RK' (4 dígitos + 2 letras)")
    print("=" * 60)
    confirm = input("\nDigite 'sim' para continuar: ").strip().lower()
    if confirm != 'sim':
        print("Migração cancelada.")
        sys.exit(0)
    migrate()
