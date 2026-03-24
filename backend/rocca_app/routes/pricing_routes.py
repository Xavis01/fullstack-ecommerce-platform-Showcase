from flask import Blueprint, request, jsonify
from ..models import db, PricingItem
from flask_jwt_extended import jwt_required
from ..routes.admin_routes import admin_required

pricing_bp = Blueprint('pricing', __name__)

@pricing_bp.route('/list', methods=['GET'])
@jwt_required()
@admin_required
def get_pricing_items():
    try:
        items = PricingItem.query.order_by(PricingItem.created_at.desc()).all()
        result = []
        for item in items:
            result.append({
                'id': item.id,
                'name': item.name,
                'cost': float(item.cost or 0),
                'price': float(item.price or 0),
                'subsidy_frete': float(item.subsidy_frete or 0),
                'ads': float(item.ads or 0)
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pricing_bp.route('/create', methods=['POST'])
@jwt_required()
@admin_required
def create_pricing_item():
    try:
        data = request.json
        # Default subsidy as requested
        new_item = PricingItem(
            name=data.get('name', ''),
            cost=data.get('cost', 0),
            price=data.get('price', 0),
            subsidy_frete=data.get('subsidy_frete', 10), # Default 10 if not provided
            ads=data.get('ads', 0)
        )
        db.session.add(new_item)
        db.session.commit()
        return jsonify({'message': 'Item created', 'id': new_item.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@pricing_bp.route('/update/<int:id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_pricing_item(id):
    try:
        item = PricingItem.query.get(id)
        if not item:
            return jsonify({'message': 'Item not found'}), 404
        
        data = request.json
        if 'name' in data: item.name = data['name']
        if 'cost' in data: item.cost = data['cost']
        if 'price' in data: item.price = data['price']
        if 'subsidy_frete' in data: item.subsidy_frete = data['subsidy_frete']
        if 'ads' in data: item.ads = data['ads']
        
        db.session.commit()
        return jsonify({'message': 'Item updated'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@pricing_bp.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_pricing_item(id):
    try:
        item = PricingItem.query.get(id)
        if not item:
            return jsonify({'message': 'Item not found'}), 404
            
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': 'Item deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
