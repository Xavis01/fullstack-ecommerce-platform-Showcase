# backend/rocca_app/routes/admin_coupon_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..models import db, Coupon, ProductCoupon, CategoryCoupon, CollectionCoupon
from .admin_routes import admin_required
from datetime import datetime

admin_coupon_routes = Blueprint('admin_coupon_routes', __name__)

def safe_int(val):
    if val is None or val == "" or str(val).strip() == "":
        return None
    try:
        res = int(val)
        return res if res > 0 else None # Trata 0 como "sem limite" (None)
    except:
        return None

def safe_decimal(val):
    if val is None or val == "" or str(val).strip() == "":
        return None
    try:
        from decimal import Decimal
        return Decimal(str(val))
    except:
        return None

@admin_coupon_routes.route('/admin/coupons/create', methods=['POST'])
@jwt_required()
@admin_required
def create_coupon():
    data = request.get_json()
    
    nome = data.get('nome')
    valor = data.get('valor')
    
    if not nome or valor is None:
        return jsonify({'error': 'Nome e valor são obrigatórios'}), 400
        
    porcentagem = data.get('porcentagem', True)
    
    data_inicio = None
    if data.get('data_inicio'):
        try:
            data_inicio = datetime.fromisoformat(data['data_inicio'].replace('Z', '+00:00'))
        except:
            pass
            
    data_fim = None
    if data.get('data_fim'):
        try:
            data_fim = datetime.fromisoformat(data['data_fim'].replace('Z', '+00:00'))
        except:
            pass
            
    coupon = Coupon(
        nome=nome,
        descricao=data.get('descricao'),
        porcentagem=porcentagem,
        valor=valor,
        frete_gratis=data.get('frete_gratis', False),
        is_active=data.get('is_active', False),
        data_inicio=data_inicio,
        data_fim=data_fim,
        gasto_minimo=safe_decimal(data.get('gasto_minimo')),
        gasto_maximo=safe_decimal(data.get('gasto_maximo')),
        uso_individual=data.get('uso_individual', True),
        excluir_item_com_desconto=data.get('excluir_item_com_desconto', True),
        produtos=data.get('produtos', False),
        excluir_produtos=data.get('excluir_produtos', False),
        categorias=data.get('categorias', False),
        excluir_categorias=data.get('excluir_categorias', False),
        colecoes=data.get('colecoes', False),
        excluir_colecoes=data.get('excluir_colecoes', False),
        limite_uso=safe_int(data.get('limite_uso')),
        limite_por_conta=safe_int(data.get('limite_por_conta'))
    )
    
    db.session.add(coupon)
    db.session.flush()
    
    products_data = data.get('product_coupons', [])
    for p in products_data:
        pc = ProductCoupon(
            coupon_id=coupon.id,
            product_id=p['product_id'],
            product_name=p.get('product_name'),
            coupon_name=coupon.nome,
            excluir=p.get('excluir', False)
        )
        db.session.add(pc)
        
    categories_data = data.get('category_coupons', [])
    for c in categories_data:
        cc = CategoryCoupon(
            coupon_id=coupon.id,
            category_id=c['category_id'],
            category_name=c.get('category_name'),
            coupon_name=coupon.nome,
            excluir=c.get('excluir', False)
        )
        db.session.add(cc)
        
    collections_data = data.get('collection_coupons', [])
    for col in collections_data:
        colc = CollectionCoupon(
            coupon_id=coupon.id,
            collection_id=col['collection_id'],
            collection_name=col.get('collection_name'),
            coupon_name=coupon.nome,
            excluir=col.get('excluir', False)
        )
        db.session.add(colc)
        
    db.session.commit()
    
    return jsonify({'message': f'Cupom "{nome}" criado com sucesso', 'id': coupon.id}), 201

@admin_coupon_routes.route('/admin/coupons/list', methods=['GET'])
@jwt_required()
@admin_required
def list_coupons():
    coupons = Coupon.query.order_by(Coupon.id.desc()).all()
    output = []
    for c in coupons:
        output.append({
            'id': c.id,
            'nome': c.nome,
            'valor': float(c.valor),
            'porcentagem': c.porcentagem,
            'is_active': c.is_active,
            'vezes_usado': c.vezes_usado
        })
    return jsonify(output), 200

@admin_coupon_routes.route('/admin/coupons/get/<int:coupon_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_coupon(coupon_id):
    coupon = Coupon.query.get(coupon_id)
    if not coupon:
        return jsonify({'error': 'Cupom não encontrado'}), 404
        
    out = {
        'id': coupon.id,
        'nome': coupon.nome,
        'descricao': coupon.descricao,
        'porcentagem': coupon.porcentagem,
        'valor': float(coupon.valor),
        'frete_gratis': coupon.frete_gratis,
        'is_active': coupon.is_active,
        'data_inicio': coupon.data_inicio.isoformat() if coupon.data_inicio else None,
        'data_fim': coupon.data_fim.isoformat() if coupon.data_fim else None,
        'gasto_minimo': float(coupon.gasto_minimo) if coupon.gasto_minimo else None,
        'gasto_maximo': float(coupon.gasto_maximo) if coupon.gasto_maximo else None,
        'uso_individual': coupon.uso_individual,
        'excluir_item_com_desconto': coupon.excluir_item_com_desconto,
        'produtos': coupon.produtos,
        'excluir_produtos': coupon.excluir_produtos,
        'categorias': coupon.categorias,
        'excluir_categorias': coupon.excluir_categorias,
        'colecoes': coupon.colecoes,
        'excluir_colecoes': coupon.excluir_colecoes,
        'limite_uso': coupon.limite_uso,
        'limite_por_conta': coupon.limite_por_conta,
        
        'product_coupons': [{'product_id': pc.product_id, 'product_name': pc.product_name, 'excluir': pc.excluir} for pc in coupon.product_coupons],
        'category_coupons': [{'category_id': cc.category_id, 'category_name': cc.category_name, 'excluir': cc.excluir} for cc in coupon.category_coupons],
        'collection_coupons': [{'collection_id': calc.collection_id, 'collection_name': calc.collection_name, 'excluir': calc.excluir} for calc in coupon.collection_coupons],
    }
    return jsonify(out), 200

@admin_coupon_routes.route('/admin/coupons/toggle_active/<int:coupon_id>', methods=['PATCH'])
@jwt_required()
@admin_required
def toggle_active_coupon(coupon_id):
    coupon = Coupon.query.get(coupon_id)
    if not coupon:
        return jsonify({'error': 'Cupom não encontrado'}), 404
    
    data = request.get_json()
    new_active = data.get('is_active')
    if new_active is not None:
        coupon.is_active = new_active
        db.session.commit()
        return jsonify({'message': 'Status atualizado com sucesso', 'is_active': coupon.is_active}), 200
    
    return jsonify({'error': 'Parâmetro is_active é obrigatório'}), 400

@admin_coupon_routes.route('/admin/coupons/update/<int:coupon_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_coupon(coupon_id):
    coupon = Coupon.query.get(coupon_id)
    if not coupon:
        return jsonify({'error': 'Cupom não encontrado'}), 404
        
    data = request.get_json()
    
    coupon.nome = data.get('nome', coupon.nome)
    coupon.descricao = data.get('descricao')
    coupon.porcentagem = data.get('porcentagem', coupon.porcentagem)
    coupon.valor = data.get('valor', coupon.valor)
    coupon.frete_gratis = data.get('frete_gratis', coupon.frete_gratis)
    coupon.is_active = data.get('is_active', coupon.is_active)
    
    if 'data_inicio' in data:
        if data['data_inicio']:
            try:
                coupon.data_inicio = datetime.fromisoformat(data['data_inicio'].replace('Z', '+00:00'))
            except:
                pass
        else:
            coupon.data_inicio = None
            
    if 'data_fim' in data:
        if data['data_fim']:
            try:
                coupon.data_fim = datetime.fromisoformat(data['data_fim'].replace('Z', '+00:00'))
            except:
                pass
        else:
            coupon.data_fim = None
            
    coupon.gasto_minimo = safe_decimal(data.get('gasto_minimo'))
    coupon.gasto_maximo = safe_decimal(data.get('gasto_maximo'))
    coupon.uso_individual = data.get('uso_individual', coupon.uso_individual)
    coupon.excluir_item_com_desconto = data.get('excluir_item_com_desconto', coupon.excluir_item_com_desconto)
    coupon.produtos = data.get('produtos', coupon.produtos)
    coupon.excluir_produtos = data.get('excluir_produtos', coupon.excluir_produtos)
    coupon.categorias = data.get('categorias', coupon.categorias)
    coupon.excluir_categorias = data.get('excluir_categorias', coupon.excluir_categorias)
    coupon.colecoes = data.get('colecoes', coupon.colecoes)
    coupon.excluir_colecoes = data.get('excluir_colecoes', coupon.excluir_colecoes)
    coupon.limite_uso = safe_int(data.get('limite_uso'))
    coupon.limite_por_conta = safe_int(data.get('limite_por_conta'))
    
    ProductCoupon.query.filter_by(coupon_id=coupon.id).delete()
    CategoryCoupon.query.filter_by(coupon_id=coupon.id).delete()
    CollectionCoupon.query.filter_by(coupon_id=coupon.id).delete()
    
    products_data = data.get('product_coupons', [])
    for p in products_data:
        pc = ProductCoupon(
            coupon_id=coupon.id,
            product_id=p['product_id'],
            product_name=p.get('product_name'),
            coupon_name=coupon.nome,
            excluir=p.get('excluir', False)
        )
        db.session.add(pc)
        
    categories_data = data.get('category_coupons', [])
    for c in categories_data:
        cc = CategoryCoupon(
            coupon_id=coupon.id,
            category_id=c['category_id'],
            category_name=c.get('category_name'),
            coupon_name=coupon.nome,
            excluir=c.get('excluir', False)
        )
        db.session.add(cc)
        
    collections_data = data.get('collection_coupons', [])
    for col in collections_data:
        colc = CollectionCoupon(
            coupon_id=coupon.id,
            collection_id=col['collection_id'],
            collection_name=col.get('collection_name'),
            coupon_name=coupon.nome,
            excluir=col.get('excluir', False)
        )
        db.session.add(colc)
    
    db.session.commit()
    return jsonify({'message': 'Cupom atualizado com sucesso'}), 200

@admin_coupon_routes.route('/admin/coupons/delete/<int:coupon_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_coupon(coupon_id):
    coupon = Coupon.query.get(coupon_id)
    if not coupon:
        return jsonify({'error': 'Cupom não encontrado'}), 404
        
    db.session.delete(coupon)
    db.session.commit()
    
    return jsonify({'message': 'Cupom deletado com sucesso'}), 200
