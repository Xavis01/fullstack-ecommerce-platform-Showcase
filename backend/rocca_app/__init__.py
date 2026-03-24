import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from flask import Flask
from flask import request
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import DevelopmentConfig, ProductionConfig
import os
import time


# Inicializa extensões
db = SQLAlchemy()
mail = Mail()

# Rate Limiter global (anti-DDoS / brute force)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["300 per day", "60 per hour", "20 per minute"],
    storage_uri="memory://",
)

def create_app():
    app = Flask(__name__)
    

    flask_env = os.getenv("FLASK_ENV", "development")
    upload_mode = os.getenv("UPLOAD_MODE")
    vps_upload_url = os.getenv("VPS_UPLOAD_URL")
    print(f"VPS_UPLOAD_URL carregado: {vps_upload_url}")
    print(f"FLASK_ENV carregado: {flask_env}")
    print(f"UPLOAD_MODE carregado: {upload_mode}")

    jwt = JWTManager(app)
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB
    if flask_env == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    db.init_app(app)
    mail.init_app(app)
    # CORS restrito ao domínio do frontend
    allowed_origins = [
        os.getenv("FRONTEND_URL", "http://localhost:5173"),
        "http://localhost:5173",
        "http://localhost:3000",
    ]
    
    # Em desenvolvimento, permite todas as origens para facilitar acesso mobile pela rede local
    cors_origins = "*" if flask_env != "production" else allowed_origins

    CORS(app, resources={
        r"/api/*": {
            "origins": cors_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
        }
    })

    # Inicializa o limiter na app
    limiter.init_app(app)

    from .models import User, Product, Order, OrderItem, EmailVerificationToken
    
    from .routes.admin_category_routes import admin_category_routes
    from .routes.admin_images_routes import admin_images_routes
    from .routes.admin_order_routes import admin_order_routes
    from .routes.admin_product_routes import admin_product_routes
    from .routes.admin_routes import admin_routes
    from .routes.admin_utils_routes import admin_utils_routes
    from .routes.admin_collection_routes import admin_collection_routes
    from .routes.admin_coupon_routes import admin_coupon_routes
    from .routes.admin_shipping_routes import admin_shipping_routes
    
    from .routes.user_cart_routes import user_cart_routes
    from .routes.user_product_routes import user_product_routes
    from .routes.user_routes import user_routes
    from .routes.fast_sale_routes import fast_sale_routes
    from .routes.webhook_routes import webhook_routes
    from .routes.public_coupon_routes import public_coupon_routes
    from .routes.shipping_routes import shipping_routes

    app.register_blueprint(admin_category_routes, url_prefix="/api")
    app.register_blueprint(admin_images_routes, url_prefix="/api")
    app.register_blueprint(admin_order_routes, url_prefix="/api")
    app.register_blueprint(admin_product_routes, url_prefix="/api")
    app.register_blueprint(admin_routes, url_prefix="/api")
    app.register_blueprint(admin_utils_routes, url_prefix="/api")
    app.register_blueprint(admin_collection_routes, url_prefix="/api")
    app.register_blueprint(admin_coupon_routes, url_prefix="/api")
    app.register_blueprint(admin_shipping_routes, url_prefix="/api")
    
    app.register_blueprint(user_cart_routes, url_prefix="/api")
    app.register_blueprint(user_product_routes, url_prefix="/api")
    app.register_blueprint(user_routes, url_prefix="/api")
    app.register_blueprint(fast_sale_routes, url_prefix="/api")
    app.register_blueprint(webhook_routes, url_prefix="/api")
    app.register_blueprint(public_coupon_routes, url_prefix="/api")
    app.register_blueprint(shipping_routes, url_prefix="/api")
    
    from .routes.pricing_routes import pricing_bp
    app.register_blueprint(pricing_bp, url_prefix="/api/admin/pricing")

    @app.before_request
    def before_request():
        request.start_time = time.time()

    @app.after_request
    def after_request(response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            print(f"[{request.method}] {request.path} levou {duration:.4f} segundos")

        # ── Headers de segurança ──────────────────────────────────────────
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        flask_env = os.getenv("FLASK_ENV", "development")
        if flask_env == "production":
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        return response

    #print("USANDO DB:", app.config['SQLALCHEMY_DATABASE_URI'])

    return app  