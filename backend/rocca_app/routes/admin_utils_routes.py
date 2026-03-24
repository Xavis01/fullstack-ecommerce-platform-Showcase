# backend/rocca_app/routes/admin_utils_routes.py

from flask import Blueprint, request, jsonify, current_app
import os
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..models import db, Product
import secrets
from ..routes.admin_routes import admin_required
from datetime import datetime

admin_utils_routes = Blueprint('admin_utils_routes', __name__)
flask_env = os.getenv("FLASK_ENV", "development")


################################### Endpoints para Agendar publicações ##################################
@admin_utils_routes.route('/admin/products/schedule_publish/', methods=['POST'])
@jwt_required()
@admin_required
def schedule_publish():
    data = request.json
    ids = data.get('ids')                 # Exemplo: [1, 2, 3]
    scheduled_at = data.get('scheduled_publish_at')   # Exemplo: "2024-07-27T14:00:00"

    if not ids or not scheduled_at:
        return jsonify({'error': 'IDs e data/hora são obrigatórios'}), 400

    try:
        scheduled_dt = datetime.fromisoformat(scheduled_at)
    except Exception as e:
        return jsonify({'error': 'Formato de data/hora inválido. Use UTC em formato ISO.'}), 400

    updated = []
    for pid in ids:
        product = Product.query.get(pid)
        if product:
            product.scheduled_publish_at = scheduled_dt
            product.is_scheduled = True
            product.is_public = False
            updated.append(product.id)
    db.session.commit()

    return jsonify({
        'msg': f'Produtos agendados: {updated}',
        'scheduled_for': scheduled_at
    })
#######################################################################################################