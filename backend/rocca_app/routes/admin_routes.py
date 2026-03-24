# backend/rocca_app/routes/admin_routes.py

from flask import Blueprint, request, jsonify, current_app
import re
from werkzeug.utils import secure_filename
import os
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..models import db, Product, User, ProductVariant, Order, OrderItem, ProductCategory, Category, CartItem, ProductImage
from ..utils.upload_utils import save_image, delete_remote_image
import secrets
from datetime import datetime

admin_routes = Blueprint('admin_routes', __name__)
flask_env = os.getenv("FLASK_ENV", "development")


#################### Middleware simples para checar se  é admin ###########################
def admin_required(fn):
    from functools import wraps

    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if not claims.get('is_admin'):
            return jsonify({'error': 'Acesso restrito a administradores.'}), 403
        return fn(*args, **kwargs)

    return wrapper
##########################################################################################


##################### Listagem de Usuários ###############################
@admin_routes.route('/admin/users/list', methods=['GET'])
@jwt_required()
@admin_required
def list_users():
    is_admin = request.args.get('is_admin')
    
    query = User.query

    if is_admin is not None:
        # Convert string 'true'/'false' or '1'/'0' to boolean
        if is_admin.lower() in ['true', '1']:
            query = query.filter_by(is_admin=True)
        elif is_admin.lower() in ['false', '0']:
            query = query.filter_by(is_admin=False)

    users = query.all()
    output = []
    for user in users:
        output.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "is_admin" : user.is_admin,
            "created_at": user.created_at
        })
    return jsonify(output)
###########################################################################


##################### Criar Usuário ###############################
@admin_routes.route('/admin/users/create', methods=['POST'])
@jwt_required()
@admin_required
def create_user():
    from ..utils.password_utils import hash_password
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    is_admin = data.get('is_admin', False)

    if not name or not email or not password:
        return jsonify({'error': 'Nome, email e senha são obrigatórios'}), 400

    if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+$", email):
        return jsonify({'error': 'Formato de e-mail inválido'}), 400

    if not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s\'-]+$", name):
        return jsonify({'error': 'O nome não pode conter caracteres especiais ou números'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email já cadastrado'}), 400

    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        is_admin=is_admin
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Usuário criado com sucesso', 'id': user.id}), 201
###########################################################################


##################### Atualizar Usuário ###############################
@admin_routes.route('/admin/users/update/<int:user_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_user(user_id):
    from ..utils.password_utils import hash_password
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    is_admin = data.get('is_admin', user.is_admin)

    if not name or not email:
        return jsonify({'error': 'Nome e email são obrigatórios'}), 400

    if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+$", email):
        return jsonify({'error': 'Formato de e-mail inválido'}), 400

    if not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s\'-]+$", name):
        return jsonify({'error': 'O nome não pode conter caracteres especiais ou números'}), 400

    # Verifica duplicação de email (exceto o próprio usuário)
    existing = User.query.filter_by(email=email).first()
    if existing and existing.id != user_id:
        return jsonify({'error': 'Email já está em uso por outro usuário'}), 400

    user.name = name
    user.email = email
    user.is_admin = is_admin
    if password:
        user.password_hash = hash_password(password)

    db.session.commit()
    return jsonify({'message': 'Usuário atualizado com sucesso'}), 200
###########################################################################


##################### Excluir Usuário ###############################
@admin_routes.route('/admin/users/delete/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Usuário excluído com sucesso'}), 200
###########################################################################