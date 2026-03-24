# backend/rocca_app/routes/admin_collection_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..models import db, Collection
from .admin_routes import admin_required

admin_collection_routes = Blueprint('admin_collection_routes', __name__)

@admin_collection_routes.route('/admin/collections/create', methods=['POST'])
@jwt_required()
@admin_required
def create_collection():
    data = request.get_json()
    name = data.get('name')

    if not name:
        return jsonify({'error': 'Nome da coleção é obrigatório'}), 400

    existing = Collection.query.filter_by(name=name).first()
    if existing:
        return jsonify({'error': 'Coleção já existe'}), 400

    collection = Collection(name=name)
    db.session.add(collection)
    db.session.commit()

    return jsonify({'message': f'Coleção "{name}" criada com sucesso'}), 201

@admin_collection_routes.route('/admin/collections/list', methods=['GET'])
@jwt_required()
@admin_required
def list_collections():
    collections = Collection.query.order_by(Collection.name.asc()).all()
    output = []
    for col in collections:
        count = len(col.products)
        output.append({
            "id": col.id, 
            "name": col.name,
            "product_count": count
        })
    return jsonify(output), 200

@admin_collection_routes.route('/admin/collections/update/<int:collection_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_collection(collection_id):
    collection = Collection.query.get(collection_id)
    if not collection:
        return jsonify({'error': 'Coleção não encontrada'}), 404

    data = request.get_json()
    new_name = data.get('name')

    if not new_name:
        return jsonify({'error': 'Novo nome é obrigatório'}), 400

    existing = Collection.query.filter_by(name=new_name).first()
    if existing and existing.id != collection.id:
        return jsonify({'error': 'Já existe outra coleção com esse nome'}), 400

    collection.name = new_name
    db.session.commit()

    return jsonify({'message': 'Coleção atualizada com sucesso'}), 200

@admin_collection_routes.route('/admin/collections/delete/<int:collection_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_collection(collection_id):
    collection = Collection.query.get(collection_id)
    if not collection:
        return jsonify({'error': 'Coleção não encontrada'}), 404

    if collection.products:
        return jsonify({'error': 'Não é possível deletar: coleção está associada a produtos'}), 400

    db.session.delete(collection)
    db.session.commit()

    return jsonify({'message': 'Coleção deletada com sucesso'}), 200

@admin_collection_routes.route('/admin/collections/<int:collection_id>/add_products', methods=['POST'])
@jwt_required()
@admin_required
def add_products_to_collection(collection_id):
    collection = Collection.query.get(collection_id)
    if not collection:
        return jsonify({'error': 'Coleção não encontrada'}), 404

    data = request.get_json()
    product_ids = data.get('product_ids', [])
    if not isinstance(product_ids, list):
        return jsonify({'error': 'A lista de produtos é inválida'}), 400

    from ..models import Product, ProductCollection

    added_count = 0
    for pid in product_ids:
        product = Product.query.get(pid)
        if not product:
            continue
        
        # Check if relation already exists
        existing = ProductCollection.query.filter_by(product_id=product.id, collection_id=collection.id).first()
        if not existing:
            pcol = ProductCollection(
                product_id=product.id,
                collection_id=collection.id,
                product_name=product.name,
                collection_name=collection.name
            )
            db.session.add(pcol)
            # Make sure product logic for single string collection field is kept in sync
            product.collection = collection.name
            added_count += 1

    db.session.commit()
    return jsonify({'message': f'{added_count} produto(s) adicionados à coleção com sucesso.'}), 200
