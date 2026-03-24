"""
Script de migração para criar a tabela email_verification_tokens.
Execute uma vez após as mudanças no models.py:
    python backend/alter_db_email_verification.py
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rocca_app import create_app, db
from rocca_app.models import EmailVerificationToken

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ Tabela 'email_verification_tokens' criada (ou já existia).")
