# backend/publish_scheduled_products.py
import datetime
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import DevelopmentConfig, ProductionConfig
from backend.rocca_app import create_app, db
from backend.rocca_app.models import Product


def publish_scheduled_products():
    app = create_app()
    flask_env = os.getenv("FLASK_ENV", "development")

    if flask_env == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    with app.app_context():
        now = datetime.datetime.now()
        products = Product.query.filter(
            Product.is_scheduled == True,
            Product.scheduled_publish_at != None,
            Product.scheduled_publish_at <= now
        ).all()

        if not products:
            print("[manual] Nenhum produto para publicar.")
            return

        for product in products:
            print(f"[manual] Publicando {product.id} - {product.name}")
            product.is_public = True
            product.is_scheduled = False
            product.scheduled_publish_at = None

        db.session.commit()
        print(f"[manual] {len(products)} produto(s) publicados.")


if __name__ == "__main__":
    publish_scheduled_products()
