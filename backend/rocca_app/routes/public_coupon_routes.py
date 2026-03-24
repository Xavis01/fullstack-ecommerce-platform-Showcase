from flask import Blueprint, request, jsonify
from datetime import datetime
from ..models import db, Coupon, Cart, CartItem, ProductVariant
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import limiter

public_coupon_routes = Blueprint('public_coupon_routes', __name__)

def check_coupon_validity(coupon_code, cart_total, user_id=None):
    if not coupon_code:
        return {"valid": False, "message": "Código de cupom não fornecido."}

    coupon = Coupon.query.filter(Coupon.nome.ilike(coupon_code)).first()
    
    if not coupon:
        return {"valid": False, "message": "Cupom não encontrado."}
        
    if not coupon.is_active:
        return {"valid": False, "message": "Este cupom não está ativo."}
        
    now = datetime.utcnow()
    
    if coupon.data_inicio and now < coupon.data_inicio:
        return {"valid": False, "message": "O período deste cupom ainda não começou."}
        
    if coupon.data_fim and now > coupon.data_fim:
        return {"valid": False, "message": "Este cupom já expirou."}
        
    if coupon.gasto_minimo and cart_total < float(coupon.gasto_minimo):
        return {"valid": False, "message": f"O valor mínimo para este cupom é R$ {float(coupon.gasto_minimo):.2f}."}
        
    if coupon.gasto_maximo and cart_total > float(coupon.gasto_maximo):
         return {"valid": False, "message": f"O valor máximo para este cupom é R$ {float(coupon.gasto_maximo):.2f}."}
         
    if coupon.limite_uso is not None and coupon.vezes_usado >= coupon.limite_uso:
         return {"valid": False, "message": "Este cupom já atingiu o limite de utilizações."}

    # Verifica limite por conta se o usuário estiver logado
    if user_id and coupon.limite_por_conta is not None:
        from ..models import Order
        try:
            user_id_int = int(user_id)
        except Exception:
            user_id_int = user_id

        usage_count = Order.query.filter(
            Order.user_id == user_id_int,
            Order.coupon_id == coupon.id,
            Order.payment_status != 'rejected'
        ).count()
        
        if usage_count >= coupon.limite_por_conta:
            return {"valid": False, "message": f"Você já atingiu o limite de uso deste cupom ({coupon.limite_por_conta}x)."}

    return {"valid": True, "coupon": coupon}

@public_coupon_routes.route('/public-coupons/validate', methods=['POST'])
@jwt_required(optional=True)
@limiter.limit("20 per minute")
def validate_coupon():
    """
    Valida um cupom com base no carrinho atual
    Recebe list de itens com {product_id, variant_id, price, quantity} ou apenas o valor total
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    coupon_code = data.get('coupon_code')
    cart_items = data.get('cart_items', [])
    
    if not coupon_code:
        return jsonify({"valid": False, "message": "Código não fornecido."}), 400
        
    if not cart_items or len(cart_items) == 0:
         return jsonify({"valid": False, "message": "O carrinho está vazio."}), 400
         
    # 1. Calcula os totais do carrinho e lista os produtos/categorias pra validar regras do DB
    cart_total = 0.0
    products_in_cart = []
    categories_in_cart = []
    collections_in_cart = []
    
    for item in cart_items:
        # Se for um guest cart, usamos os dados enviados. Se for api call, também (passam do frontend)
        # Idealmente o price seria revalidado db, mas pra validação rápida podemos usar o passado
        variant = ProductVariant.query.get(item.get('variant_id'))
        if not variant:
            continue
            
        product = variant.product
        quantity = int(item.get('quantity', 1))
        price = float(product.price)
        subtotal = price * quantity
        cart_total += subtotal
        
        products_in_cart.append({"product": product, "subtotal": subtotal, "quantity": quantity})
        for pc in product.product_categories:
            categories_in_cart.append(pc.category_id)
        for pcol in product.product_collections:
             collections_in_cart.append(pcol.collection_id)


    # 2. Faz validações de regras básicas de data/valor:
    validity = check_coupon_validity(coupon_code, cart_total, user_id=user_id)
    if not validity.get('valid'):
        return jsonify(validity), 400
        
    coupon = validity.get('coupon')
    
    # 3. Faz validação de Produtos/Categorias/Coleções
    eligible_total = 0.0
    has_any_eligible = False
    
    # Busca relações
    included_products = [pc.product_id for pc in coupon.product_coupons if not pc.excluir]
    excluded_products = [pc.product_id for pc in coupon.product_coupons if pc.excluir]
    
    included_categories = [cc.category_id for cc in coupon.category_coupons if not cc.excluir]
    excluded_categories = [cc.category_id for cc in coupon.category_coupons if cc.excluir]
    
    included_collections = [cc.collection_id for cc in coupon.collection_coupons if not cc.excluir]
    excluded_collections = [cc.collection_id for cc in coupon.collection_coupons if cc.excluir]
    
    
    for item in products_in_cart:
        p = item['product']
        subtotal = item['subtotal']
        is_eligible = True
        
        # Exclusões batem primeiro
        if coupon.excluir_produtos and p.id in excluded_products:
            is_eligible = False
            
        if is_eligible and coupon.excluir_categorias:
            p_cats = [pc.category_id for pc in p.product_categories]
            if any(c in excluded_categories for c in p_cats):
                is_eligible = False
                
        if is_eligible and coupon.excluir_colecoes:
            p_cols = [pc.collection_id for pc in p.product_collections]
            if any(c in excluded_collections for c in p_cols):
                 is_eligible = False
                 
        if not is_eligible:
            continue
            
        # Avalia Inclusões se existirem marcadas
        needed_inclusion = False
        included = False
        
        if coupon.produtos:
            needed_inclusion = True
            if p.id in included_products:
                included = True
                
        if coupon.categorias:
            needed_inclusion = True
            p_cats = [pc.category_id for pc in p.product_categories]
            if any(c in included_categories for c in p_cats):
                included = True
                
        if coupon.colecoes:
            needed_inclusion = True
            p_cols = [pc.collection_id for pc in p.product_collections]
            if any(c in included_collections for c in p_cols):
                 included = True
                 
        if needed_inclusion and not included:
            is_eligible = False
            
        if is_eligible:
             eligible_total += subtotal
             has_any_eligible = True

             
    if not has_any_eligible:
        return jsonify({"valid": False, "message": "Este cupom não se aplica aos itens do seu carrinho."}), 400
        
    
    # 4. Calcular o desconto baseado na base elegível ou no total (se excluir_item_com_desconto = true, apenas apply no eligible_total)
    base_calc = eligible_total if coupon.excluir_item_com_desconto else cart_total
    
    discount_amount = 0.0
    if coupon.porcentagem:
        discount_amount = base_calc * (float(coupon.valor) / 100.0)
    else:
        # Se for valor fixo, o próprio desconto fixo (limitado pelo valor dos itens elegíveis)
        discount_amount = min(float(coupon.valor), base_calc)
        
    return jsonify({
        "valid": True,
        "coupon_id": coupon.id,
        "coupon_code": coupon.nome,
        "discount_amount": float(discount_amount),
        "frete_gratis": coupon.frete_gratis,
        "porcentagem": coupon.porcentagem,
        "valor": float(coupon.valor),
        "descricao": coupon.descricao,
        "message": "Cupom aplicado com sucesso!"
    }), 200
