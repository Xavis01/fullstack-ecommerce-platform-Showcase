from sqlalchemy import text
from rocca_app import create_app, db

def migrate():
    app = create_app()
    with app.app_context():
        with db.engine.connect() as conn:
            # Adiciona sort_order em products (caso não exista)
            try:
                conn.execute(text("ALTER TABLE products ADD COLUMN sort_order INTEGER NOT NULL DEFAULT 9999"))
                conn.commit()
                print("✅ Coluna 'sort_order' adicionada em products")
            except Exception as e:
                print(f"ℹ️  sort_order: {e}")

            # Adiciona highlight_order em product_categories (caso não exista)
            try:
                conn.execute(text("ALTER TABLE product_categories ADD COLUMN highlight_order INTEGER NOT NULL DEFAULT 9999"))
                conn.commit()
                print("✅ Coluna 'highlight_order' adicionada em product_categories")
            except Exception as e:
                print(f"ℹ️  highlight_order: {e}")

        print("✅ Migração concluída!")

if __name__ == '__main__':
    migrate()
