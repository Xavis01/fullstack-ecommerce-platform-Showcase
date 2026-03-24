# backend/rocca_app/routes/admin_order_routes.py

from flask import Blueprint, request, jsonify, current_app
import os
from datetime import timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..models import db, Order, OrderItem
from ..routes.admin_routes import admin_required

admin_order_routes = Blueprint('admin_order_routes', __name__)
flask_env = os.getenv("FLASK_ENV", "development")


####################### Listagem de Pedidos ###############################
@admin_order_routes.route('/admin/orders/list', methods=['GET'])
@jwt_required()
@admin_required
def get_all_orders():
    from sqlalchemy.orm import joinedload
    
    orders = Order.query.options(joinedload(Order.user)).order_by(Order.created_at.desc()).all()
    orders_list = []

    for order in orders:
        # order.user is already loaded
        customer_name = order.user.name if order.user else 'Desconhecido'
        customer_email = order.user.email if order.user else 'N/A'
        
        order_info = {
            'order_id': order.id,
            'customer_name': customer_name,
            'customer_email': customer_email,
            'date': (order.created_at - timedelta(hours=3)).strftime('%d/%m/%Y %H:%M') if order.created_at else 'N/A',
            'total': float(order.total) if order.total is not None else 0.0,
            'paid': order.is_paid,
            'shipping_service_name': order.shipping_service_name,
            'shipping_price': float(order.shipping_price) if order.shipping_price else 0.0,
        }
        orders_list.append(order_info)

    return jsonify(orders_list), 200
#########################################################################


######################## Pedido Detalhado ################################
@admin_order_routes.route('/admin/orders/detail/<string:order_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_order_details(order_id):
    from sqlalchemy.orm import joinedload
    
    order = Order.query.options(
        joinedload(Order.user),
        joinedload(Order.order_items).joinedload(OrderItem.product),
        joinedload(Order.order_items).joinedload(OrderItem.product_variant)
    ).get(order_id)
    
    if not order:
        return jsonify({'error': 'Pedido não encontrado.'}), 404

    customer_name = order.user.name if order.user else 'Desconhecido'
    customer_email = order.user.email if order.user else 'N/A'

    order_data = {
        'order_id': order.id,
        'customer': {
            'name': customer_name,
            'email': customer_email,
            'cpf': order.customer_cpf,
            'phone': order.user.phone if order.user else None,
        },
        'date': (order.created_at - timedelta(hours=3)).strftime('%d/%m/%Y %H:%M') if order.created_at else 'N/A',
        'is_paid': order.is_paid,
        'payment_method': order.payment_method,
        'total': float(order.total) if order.total is not None else 0.0,
        'discount_amount': float(order.discount_amount) if order.discount_amount else 0.0,
        'coupon_code': None,
        'coupon_percentage': False,
        'coupon_value': 0.0,
        'shipping': {
            'price': float(order.shipping_price) if order.shipping_price else 0.0,
            'service_name': order.shipping_service_name,
            'service_id': order.shipping_service_id,
            'delivery_time': order.shipping_delivery_time,
            'cep': order.shipping_cep,
            'address': order.shipping_address,
            'number': order.shipping_number,
            'complement': order.shipping_complement,
            'neighborhood': order.shipping_neighborhood,
            'city': order.shipping_city,
            'state': order.shipping_state,
        },
        'items': []
    }
    
    if order.coupon_id:
        from ..models import Coupon
        coupon = Coupon.query.get(order.coupon_id)
        if coupon:
             order_data['coupon_code'] = coupon.nome
             order_data['coupon_percentage'] = coupon.porcentagem
             order_data['coupon_value'] = float(coupon.valor)

    for item in order.order_items:
        variant = item.product_variant
        product = item.product
        order_data['items'].append({
            'product_name': product.name if product else 'Produto Removido',
            'variant': variant.size if variant else "N/A",
            'quantity': item.quantity,
            'price': float(item.price) if item.price is not None else 0.0,
            'subtotal': float(item.quantity * item.price) if item.price is not None else 0.0,
            'image_url': product.images[0].image_public_url if product and product.images else None
        })

    return jsonify(order_data), 200
###########################################################################


################################## Deletar Pedido ###############################
@admin_order_routes.route('/admin/orders/delete/<string:order_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_order(order_id):
    order = Order.query.get(order_id)

    if not order:
        return jsonify({'error': 'Pedido não encontrado'}), 404

    if order.is_paid:
        return jsonify({'error': 'Não é possível excluir pedidos pagos'}), 400

    db.session.delete(order)
    db.session.commit()
    return jsonify({'message': 'Pedido excluído com sucesso'}), 200
##################################################################################
