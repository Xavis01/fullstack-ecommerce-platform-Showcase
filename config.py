import os
from dotenv import load_dotenv
from pathlib import Path

# Define caminho para o .env dentro de /backend
env_path = Path(__file__).parent / "backend" / ".env"

load_dotenv(dotenv_path=env_path)

# Só carrega o .env no modo development
if os.getenv("FLASK_ENV", "development") == "development":
    print(f"Carregando .env de: {env_path}")
    

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Use FLASK_ENV para decidir o ambiente
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    if FLASK_ENV == "development":
        UPLOAD_ENV = "dev"
    else:
        UPLOAD_ENV = "prod"

    BASE_UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'backend', 'static', 'uploads')
    UPLOAD_FOLDER = os.path.join(BASE_UPLOAD_FOLDER, UPLOAD_ENV)
    print("upload:" + UPLOAD_FOLDER)

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

    # Flask-Mail (SMTP)
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    MAIL_SUPPRESS_SEND = False  # Enviar e-mails de verdade em todos os ambientes

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "max_overflow": 5,
        "pool_timeout": 30,
        "pool_recycle": 1800
    }


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DATABASE_URI")
    DEBUG = True

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("PROD_DATABASE_URI")
    DEBUG = False
