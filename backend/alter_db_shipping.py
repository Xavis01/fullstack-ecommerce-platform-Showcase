"""
Script de migração para adicionar campos de frete (shipping) e endereço
na tabela orders, e criar a tabela app_settings para persistência de tokens.

Como rodar:
    cd project_rocca
    python backend/alter_db_shipping.py
"""
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.rocca_app import create_app, db

app = create_app()

with app.app_context():
    # 1. Adicionar campos de shipping na tabela orders
    shipping_columns = [
        ("shipping_price", "DECIMAL(10,2) DEFAULT 0.00"),
        ("shipping_service_name", "VARCHAR(100) DEFAULT NULL"),
        ("shipping_service_id", "INT DEFAULT NULL"),
        ("shipping_delivery_time", "INT DEFAULT NULL"),
        ("shipping_cep", "VARCHAR(10) DEFAULT NULL"),
        ("shipping_address", "VARCHAR(255) DEFAULT NULL"),
        ("shipping_number", "VARCHAR(20) DEFAULT NULL"),
        ("shipping_complement", "VARCHAR(100) DEFAULT NULL"),
        ("shipping_neighborhood", "VARCHAR(100) DEFAULT NULL"),
        ("shipping_city", "VARCHAR(100) DEFAULT NULL"),
        ("shipping_state", "VARCHAR(2) DEFAULT NULL"),
    ]

    for col_name, col_type in shipping_columns:
        try:
            db.session.execute(db.text(
                f"ALTER TABLE orders ADD COLUMN {col_name} {col_type}"
            ))
            print(f"✅ Coluna 'orders.{col_name}' adicionada com sucesso.")
        except Exception as e:
            if "Duplicate column" in str(e) or "already exists" in str(e):
                print(f"⏩ Coluna 'orders.{col_name}' já existe, pulando.")
            else:
                print(f"❌ Erro ao adicionar 'orders.{col_name}': {e}")

    # 2. Criar tabela app_settings
    try:
        db.session.execute(db.text("""
            CREATE TABLE IF NOT EXISTS app_settings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                `key` VARCHAR(100) UNIQUE NOT NULL,
                `value` TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """))
        print("✅ Tabela 'app_settings' criada (ou já existia).")
    except Exception as e:
        print(f"❌ Erro ao criar tabela 'app_settings': {e}")

    db.session.commit()
    print("\n🎉 Migração de shipping concluída!")
