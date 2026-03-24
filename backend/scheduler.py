# backend/scheduler.py
import sys
import os
from pathlib import Path

# Adiciona a raiz do projeto ao sys.path
ROOT_DIR = Path(__file__).parent.parent  # sobe 1 nível (para project_rocca/)
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from flask_apscheduler import APScheduler
import datetime
from backend.rocca_app import db
from backend.rocca_app.models import Product

class Config(object):
    JOBS = [
        {
            'id': 'publish_scheduled_products',
            'func': 'backend.scheduler:publish_scheduled_products',
            'trigger': 'cron',
            'minute': '*',
            'second': '0'
        }
    ]
    SCHEDULER_API_ENABLED = False

scheduler = APScheduler()

def publish_scheduled_products():
    """Job executado periodicamente para publicar produtos agendados"""
    from backend.rocca_app import create_app  # Importa dentro da função para evitar conflitos
    app = create_app()

    with app.app_context():
        # Usa UTC para evitar problemas de fuso horário do servidor
        now = datetime.datetime.utcnow()
        products = Product.query.filter(
            Product.is_scheduled == True,
            Product.scheduled_publish_at != None,
            Product.scheduled_publish_at <= now
        ).all()

        if not products:
            print("[APScheduler] Nenhum produto para publicar nesse ciclo.")
            return

        for product in products:
            print(f"[APScheduler] Publicando produto {product.id} - {product.name} "
                  f"(agendado para {product.scheduled_publish_at})")
            product.is_public = True
            product.is_scheduled = False
            product.scheduled_publish_at = None

        db.session.commit()
        print(f"[APScheduler] {len(products)} produto(s) publicados com sucesso.")
