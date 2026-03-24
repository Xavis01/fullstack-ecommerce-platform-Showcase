# backend/rocca_app/routes/admin_shipping_routes.py
"""
Rotas administrativas de frete:
- Adicionar pedido ao carrinho da Melhor Envio
"""

import os
import requests as http_requests
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from ..models import db, Order, OrderItem
from ..routes.admin_routes import admin_required
from ..services.melhor_envio_service import MelhorEnvioService, MelhorEnvioError

admin_shipping_routes = Blueprint('admin_shipping_routes', __name__)


@admin_shipping_routes.route('/admin/shipping/add-to-cart/<string:order_id>', methods=['POST'])
@jwt_required()
@admin_required
def add_to_melhorenvio_cart(order_id):
    """
    Adiciona o frete de um pedido ao carrinho da Melhor Envio.
    Retorna a URL do painel para o admin ser redirecionado.
    """
    from sqlalchemy.orm import joinedload

    order = Order.query.options(
        joinedload(Order.user),
        joinedload(Order.order_items).joinedload(OrderItem.product),
        joinedload(Order.order_items).joinedload(OrderItem.product_variant)
    ).get(order_id)

    if not order:
        return jsonify({'message': 'Pedido não encontrado.'}), 404

    if not order.shipping_service_id:
        return jsonify({'message': 'Este pedido não tem serviço de frete definido (pode ser retirada).'}), 400

    if not order.shipping_cep:
        return jsonify({'message': 'CEP de entrega não informado neste pedido.'}), 400

    service = MelhorEnvioService()

    # Monta os produtos a partir dos itens do pedido
    products = []
    for item in order.order_items:
        products.append({
            "name": item.product.name if item.product else "Produto",
            "quantity": item.quantity,
            "unitary_value": float(item.price) if item.price else 0.0
        })

    # Remetente vem do .env
    from_cep = os.environ.get("ME_CEP_ORIGEM", "29090470")
    from_name = os.environ.get("ME_SENDER_NAME", "Rocca Internazionale")
    from_email = os.environ.get("ME_SENDER_EMAIL", "contato@example.com")
    from_phone = os.environ.get("ME_SENDER_PHONE", "27999999999")

    # Destinatário
    to_name = order.user.name if order.user else "Cliente"
    to_email = order.user.email if order.user else ""

    from_document = os.environ.get("ME_SENDER_DOCUMENT", "")

    payload = {
        "service": order.shipping_service_id,
        "from": {
            "name": from_name,
            "email": from_email,
            "phone": from_phone,
            "document": from_document,
            "postal_code": from_cep.replace("-", ""),
            "address": os.environ.get("ME_SENDER_ADDRESS", "Jardim Camburi"),
            "number": os.environ.get("ME_SENDER_NUMBER", "S/N"),
            "complement": os.environ.get("ME_SENDER_COMPLEMENT", ""),
            "district": os.environ.get("ME_SENDER_DISTRICT", "Jardim Camburi"),
            "city": os.environ.get("ME_SENDER_CITY", "Vitória"),
            "state_abbr": os.environ.get("ME_SENDER_STATE", "ES"),
            "country_id": "BR",
        },
        "to": {
            "name": to_name,
            "email": to_email,
            "document": order.customer_cpf or "",
            "phone": getattr(order.user, 'phone', '') or "",
            "postal_code": order.shipping_cep.replace("-", "") if order.shipping_cep else "",
            "address": order.shipping_address or "",
            "number": order.shipping_number or "S/N",
            "complement": order.shipping_complement or "",
            "district": order.shipping_neighborhood or "",
            "city": order.shipping_city or "",
            "state_abbr": order.shipping_state or "",
            "country_id": "BR",
        },
        "products": products,
        "volumes": [
            {
                "height": 10,
                "width": 15,
                "length": 20,
                "weight": max(0.3, sum(item.quantity * 0.5 for item in order.order_items))
            }
        ],
        "options": {
            "insurance_value": float(order.total) if order.total else 0.0,
            "non_commercial": True
        }
    }

    try:
        base_url = service._get_base_url()
        headers = service._get_headers()
        response = http_requests.post(
            f"{base_url}/api/v2/me/cart",
            json=payload,
            headers=headers,
            timeout=15
        )

        if response.status_code == 401:
            # Token expirado — tenta renovar
            service._refresh_token()
            headers = service._get_headers()
            response = http_requests.post(
                f"{base_url}/api/v2/me/cart",
                json=payload,
                headers=headers,
                timeout=15
            )

        if not response.ok:
            print(f"[ME CART] Erro {response.status_code}: {response.text}")
            try:
                err_msg = response.json().get("message", response.text)
            except Exception:
                err_msg = response.text
            return jsonify({
                'message': f'Erro da Melhor Envio: {err_msg}'
            }), response.status_code

        cart_item = response.json()
        print(f"[ME CART] Adicionado ao carrinho: {cart_item}")

        # URL do painel da ME para o carrinho
        if service.environment == "production":
            cart_url = "https://melhorenvio.com.br/carrinho"
        else:
            cart_url = "https://sandbox.melhorenvio.com.br/carrinho"

        return jsonify({
            'success': True,
            'cart_item': cart_item,
            'redirect_url': cart_url
        }), 200

    except MelhorEnvioError as e:
        return jsonify({'message': str(e)}), e.status_code or 500
    except Exception as e:
        print(f"[ME CART] Exceção: {e}")
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500
