# backend/rocca_app/routes/shipping_routes.py

from flask import Blueprint, request, jsonify
from ..services.melhor_envio_service import MelhorEnvioService, MelhorEnvioError
from .. import limiter

shipping_routes = Blueprint('shipping_routes', __name__)


@shipping_routes.route('/shipping/calculate', methods=['POST'])
@limiter.limit("30 per minute")
def calculate_shipping():
    """
    Calcula opções de frete a partir do CEP e lista de produtos.
    
    Body esperado:
    {
        "cep": "01001000",
        "products": [
            { "product_id": 1, "quantity": 2 },
            { "product_id": 5, "quantity": 1 }
        ]
    }
    
    Retorna:
    {
        "shipping_options": [
            {
                "id": 1,
                "name": "PAC",
                "price": 25.50,
                "delivery_time": 7,
                "company_name": "Correios",
                "company_picture": "https://..."
            },
            ...
        ]
    }
    """
    from ..models import Product

    data = request.get_json() or {}
    cep = data.get("cep", "")
    product_items = data.get("products", [])

    if not cep:
        return jsonify({"error": "CEP é obrigatório."}), 400

    if not product_items:
        return jsonify({"error": "Lista de produtos é obrigatória."}), 400

    # Monta dados reais dos produtos a partir do banco de dados
    # NUNCA confia em peso/dimensões vindos do frontend
    products_data = []
    for item in product_items:
        product_id = item.get("product_id")
        quantity = item.get("quantity", 1)

        if not product_id:
            return jsonify({"error": "product_id é obrigatório em cada item."}), 400

        product = Product.query.get(product_id)
        if not product:
            return jsonify({"error": f"Produto #{product_id} não encontrado."}), 404

        products_data.append({
            "weight": float(product.weight),
            "width": float(product.dimensionL),      # Largura
            "height": float(product.dimensionA),      # Altura
            "length": float(product.dimensionC),      # Comprimento
            "quantity": quantity,
        })

    try:
        service = MelhorEnvioService()
        options = service.calculate_shipping(cep, products_data)
        return jsonify({"shipping_options": options}), 200
    except MelhorEnvioError as e:
        status = e.status_code or 500
        return jsonify({"error": str(e), "details": e.details}), status
    except Exception as e:
        print(f"[Shipping] Erro inesperado: {e}")
        return jsonify({"error": "Erro interno ao calcular frete."}), 500
