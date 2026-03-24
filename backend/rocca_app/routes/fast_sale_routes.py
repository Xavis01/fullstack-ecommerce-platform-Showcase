from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, FastSale, FastSaleItem, Product, ProductVariant, User
from ..routes.admin_routes import admin_required
from datetime import datetime

fast_sale_routes = Blueprint('fast_sale_routes', __name__)

@fast_sale_routes.route('/fast-sales', methods=['GET'])
@jwt_required()
@admin_required
def get_fast_sales():
    from sqlalchemy.orm import joinedload
    
    # Eager load relationships to avoid N+1 queries
    query = FastSale.query.options(
        joinedload(FastSale.items).joinedload(FastSaleItem.product).joinedload(Product.images),
        joinedload(FastSale.items).joinedload(FastSaleItem.product_variant),
        joinedload(FastSale.user) 
    ).order_by(FastSale.date.desc())
    
    sales = query.all()
    output = []
    for sale in sales:
        items = []
        for item in sale.items:
            # Get cover image (is_cover=True) or first image
            product_image = None
            if item.product and item.product.images:
                # Find cover image
                cover_img = next((img for img in item.product.images if img.is_cover), None)
                if cover_img:
                    product_image = cover_img.image_public_url
                else:
                    # Fallback to first image
                    product_image = item.product.images[0].image_public_url
            
            items.append({
                'id': item.id,
                'product_id': item.product_id,
                'product_name': item.product.name if item.product else 'Produto excluído',
                'product_image': product_image,
                'product_variant_id': item.product_variant_id,
                'size': item.product_variant.size if item.product_variant else 'N/A',
                'quantity': item.quantity,
                'price': float(item.price)
            })
        
        # Use sale.user (loaded) instead of User.query.get
        created_by_name = sale.user.name if sale.user else 'Desconhecido'

        output.append({
            'id': sale.id,
            'client_name': sale.client_name,
            'total_price': float(sale.total_price),
            'pay_method': sale.pay_method,
            'date': sale.date.isoformat(),
            'created_at': sale.created_at.isoformat(),
            'created_by': sale.created_by,
            'created_by_name': created_by_name,
            'items': items
        })
    return jsonify(output), 200

@fast_sale_routes.route('/fast-sales', methods=['POST'])
@jwt_required()
@admin_required
def create_fast_sale():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    # Validação básica
    if not data.get('items'):
        return jsonify({'error': 'Nenhum item na venda'}), 400

    try:
        # Criar a venda
        new_sale = FastSale(
            client_name=data.get('client_name'),
            total_price=data.get('total_price'),
            pay_method=data.get('pay_method'),
            date=datetime.fromisoformat(data.get('date').replace('Z', '+00:00')).replace(tzinfo=None) if data.get('date') else datetime.utcnow(),
            created_by=current_user_id
        )
        db.session.add(new_sale)
        db.session.flush() # Pra pegar o ID

        # Processar itens e estoque
        for item_data in data.get('items'):
            variant = ProductVariant.query.get(item_data['product_variant_id'])
            if not variant:
                raise Exception(f"Variante {item_data['product_variant_id']} não encontrada")
            
            if variant.stock < item_data['quantity']:
                 raise Exception(f"Estoque insuficiente para {variant.product.name} ({variant.size})")

            variant.stock -= item_data['quantity']
            
            new_item = FastSaleItem(
                fast_sale_id=new_sale.id,
                product_id=item_data['product_id'],
                product_variant_id=item_data['product_variant_id'],
                quantity=item_data['quantity'],
                price=item_data['price']
            )
            db.session.add(new_item)

        db.session.commit()
        return jsonify({'message': 'Venda rápida criada com sucesso', 'id': new_sale.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@fast_sale_routes.route('/fast-sales/<int:id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_fast_sale(id):
    sale = FastSale.query.get_or_404(id)
    data = request.get_json()
    
    try:
        # 1. Restaurar estoque dos itens antigos
        for item in sale.items:
            variant = ProductVariant.query.get(item.product_variant_id)
            if variant:
                variant.stock += item.quantity
        
        # 2. Remover itens antigos
        # Como estamos limpando a lista e adicionando novos, precisamos garantir que o ORM entenda
        # A relação tem cascade="all, delete-orphan", então remover da lista deve deletar
        sale.items = []
        db.session.flush()
        
        # 3. Atualizar dados da venda
        sale.client_name = data.get('client_name', sale.client_name)
        sale.total_price = data.get('total_price', sale.total_price)
        sale.pay_method = data.get('pay_method', sale.pay_method)
        if data.get('date'):
             sale.date = datetime.fromisoformat(data.get('date').replace('Z', '+00:00')).replace(tzinfo=None)

        # 4. Adicionar novos itens e deduzir estoque
        if data.get('items'):
            for item_data in data.get('items'):
                variant = ProductVariant.query.get(item_data['product_variant_id'])
                if not variant:
                     raise Exception(f"Variante {item_data['product_variant_id']} não encontrada")
                
                # Nota: O estoque foi restaurado no passo 1, então agora validamos com o estoque "cheio"
                if variant.stock < item_data['quantity']:
                    raise Exception(f"Estoque insuficiente para {variant.product.name} ({variant.size})")

                variant.stock -= item_data['quantity']
                
                new_item = FastSaleItem(
                    fast_sale_id=sale.id,
                    product_id=item_data['product_id'],
                    product_variant_id=item_data['product_variant_id'],
                    quantity=item_data['quantity'],
                    price=item_data['price']
                )
                db.session.add(new_item)
        
        db.session.commit()
        return jsonify({'message': 'Venda atualizada com sucesso'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@fast_sale_routes.route('/fast-sales/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_fast_sale(id):
    sale = FastSale.query.get_or_404(id)
    
    try:
        # Restaurar estoque
        for item in sale.items:
            variant = ProductVariant.query.get(item.product_variant_id)
            if variant:
                variant.stock += item.quantity
        
        db.session.delete(sale)
        db.session.commit()
        return jsonify({'message': 'Venda excluída e estoque restaurado'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
