"""
Script de migração para adicionar campos de thumbnail e placeholder
na tabela product_image para otimização de imagens.

Como rodar:
    cd project_rocca
    python backend/alter_db_image_optimization.py
"""
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.rocca_app import create_app, db

app = create_app()

with app.app_context():
    columns = [
        ("thumbnail_url", "VARCHAR(255) DEFAULT NULL"),
        ("thumbnail_public_url", "VARCHAR(255) DEFAULT NULL"),
        ("placeholder_blur", "TEXT DEFAULT NULL"),
    ]

    for col_name, col_type in columns:
        try:
            db.session.execute(db.text(
                f"ALTER TABLE product_image ADD COLUMN {col_name} {col_type}"
            ))
            print(f"✅ Coluna 'product_image.{col_name}' adicionada com sucesso.")
        except Exception as e:
            if "Duplicate column" in str(e) or "already exists" in str(e):
                print(f"⏩ Coluna 'product_image.{col_name}' já existe, pulando.")
            else:
                print(f"❌ Erro ao adicionar 'product_image.{col_name}': {e}")

    db.session.commit()
    print("\n🎉 Migração de otimização de imagens concluída!")
