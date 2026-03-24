# backend/rocca_app/routes/admin_categorie_routes.py

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..models import db, Category
from ..utils.upload_utils import save_image, delete_remote_image
import secrets
from .admin_routes import admin_required


admin_category_routes = Blueprint('admin_category_routes', __name__)
flask_env = os.getenv("FLASK_ENV", "development")


########################### Criar Categoria ####################################
@admin_category_routes.route('/admin/categories/create', methods=['POST'])
@jwt_required()
@admin_required
def create_category():
    data = request.get_json()
    name = data.get('name')

    if not name:
        return jsonify({'error': 'Nome da categoria é obrigatório'}), 400

    # Impede duplicatas
    existing = Category.query.filter_by(name=name).first()
    if existing:
        return jsonify({'error': 'Categoria já existe'}), 400

    category = Category(name=name)
    db.session.add(category)
    db.session.commit()

    return jsonify({'message': f'Categoria "{name}" criada com sucesso'}), 201
################################################################################


########################### Listar Categorias ###########################
@admin_category_routes.route('/admin/categories/list', methods=['GET'])
@jwt_required()
@admin_required
def list_categories():
    categories = Category.query.order_by(Category.name.asc()).all()
    if not categories:
        return jsonify({'error': 'Não existem categorias cadastradas'})
    output = []
    for cat in categories:
        count = len(cat.products) # Usa o relacionamento viewonly definido no model
        output.append({
            "id": cat.id, 
            "name": cat.name,
            "product_count": count
        })
    return jsonify(output), 200
#########################################################################


############################### Atualizar Categoria ##################################
@admin_category_routes.route('/admin/categories/update/<int:category_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({'error': 'Categoria não encontrada'}), 404

    data = request.get_json()
    new_name = data.get('name')

    if not new_name:
        return jsonify({'error': 'Novo nome é obrigatório'}), 400

    # Verifica duplicação
    existing = Category.query.filter_by(name=new_name).first()
    if existing and existing.id != category.id:
        return jsonify({'error': 'Já existe outra categoria com esse nome'}), 400

    category.name = new_name
    db.session.commit()

    return jsonify({'message': 'Categoria atualizada com sucesso'}), 200
#####################################################################################


###################################### Deletar Categoria ###############################################
@admin_category_routes.route('/admin/categories/delete/<int:category_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({'error': 'Categoria não encontrada'}), 404

    # Verifica se tem produtos ligados
    if category.products:
        return jsonify({'error': 'Não é possível deletar: categoria está associada a produtos'}), 400

    db.session.delete(category)
    db.session.commit()

    return jsonify({'message': 'Categoria deletada com sucesso'}), 200
########################################################################################################
