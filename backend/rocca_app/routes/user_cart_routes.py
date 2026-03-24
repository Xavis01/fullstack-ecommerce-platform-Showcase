# backend/rocca_app/routes/user_cart_routes.py

from flask import Blueprint, request, jsonify
from ..models import db, Order, OrderItem, ProductVariant, Cart, CartItem, generate_order_id
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from sqlalchemy.orm import joinedload
from .. import limiter

user_cart_routes = Blueprint('user_cart_routes', __name__)


def calculate_cart_total(cart):
    return sum(item.price * item.quantity for item in cart.cart_items)


################### Adicionar ao carrinho ##############################################
@user_cart_routes.route('/cart/add', methods=['POST'])
@jwt_required()
@limiter.limit("60 per minute")
def add_to_cart():
    user_id = get_jwt_identity()
    data = request.get_json()
    product_id = data.get('product_id')
    size = data.get('size', 'Unico') or 'Unico'

    quantity = data.get('quantity', 1)

    if not product_id or not size or quantity <= 0:
        return jsonify({'error': 'Produto, tamanho e quantidade válidos são obrigatórios.'}), 400

    # Buscar a variante com base no size
    variant = ProductVariant.query.filter_by(product_id=product_id, size=size).first()
    if not variant:
        return jsonify({'error': 'Variante com esse tamanho não encontrada para o produto.'}), 404

    if variant.stock < quantity:
        return jsonify({'error': 'Estoque insuficiente para esta variante.'}), 400

    # Verifica se já existe pedido em aberto
    cart = Cart.query.filter_by(user_id=user_id, is_active=True).first()
    if not cart:
        cart = Cart(user_id=user_id, is_active=True)
        db.session.add(cart)
        db.session.commit()

    # Verifica se o item já existe no carrinho
    cart_item = CartItem.query.filter_by(
        cart_id=cart.id,
        product_id=product_id,
        product_variant_id=variant.product_variant_id
    ).first()

    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            product_variant_id=variant.product_variant_id,
            quantity=quantity,
            price=variant.product.price
        )
        db.session.add(cart_item)

    cart.total = calculate_cart_total(cart)

    db.session.commit()

    return jsonify({'message': 'Produto adicionado ao carrinho com sucesso.'}), 200

###################################################################################################


##################### Visualizar carrinho ##########################################
@user_cart_routes.route('/cart/view', methods=['GET'])
@jwt_required()
@limiter.limit("60 per minute")
def view_cart():
    from decimal import Decimal
    user_id = get_jwt_identity()

    total = Decimal('0.00')
    cart = Cart.query.options(
        joinedload(Cart.cart_items)
            .joinedload(CartItem.product_variant),
        joinedload(Cart.cart_items)
            .joinedload(CartItem.product)
    ).filter_by(user_id=user_id, is_active=True).first()

    if not cart or not cart.cart_items:
        return jsonify({'cart': [], 'total': 0.0}), 200

    cart_items = []

    for item in cart.cart_items:
        variant = item.product_variant
        product = item.product
        subtotal = item.quantity * item.price
        total += subtotal

        # Buscar imagem
        image_url = product.image_url
        if product.images:
             cover = next((img for img in product.images if img.is_cover), product.images[0])
             image_url = cover.image_public_url

        cart_items.append({
            'product_id': product.id,
            'variant_id': variant.product_variant_id,
            'name': product.name,
            'size': variant.size,
            'price': float(item.price),
            'quantity': item.quantity,
            'image_url': image_url,
            'subtotal': float(subtotal)
        })

    return jsonify({'cart': cart_items, 'total': float(total)}), 200
################################################################################


################### Finalizar Pedido (prosseguir de carrinho para pedido) ###########################################
@user_cart_routes.route('/cart/checkout', methods=['POST'])
@jwt_required()
@limiter.limit("5 per minute; 20 per hour")
def checkout_cart():
    import os
    import mercadopago
    from ..models import User

    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json() or {}
    
    print("[CHECKOUT] Iniciando checkout para user_id:", user_id)
    
    # 1. Pega o carrinho do usuário
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart or not cart.cart_items:
        return jsonify({'message': 'Carrinho vazio.'}), 400

    # 2. Dados do pagamento (vindos do frontend Brick)
    token = data.get('token')
    payment_method_id = data.get('payment_method_id')
    installments = data.get('installments', 1)
    issuer_id = data.get('issuer_id')
    coupon_code = data.get('coupon_code')
    
    # 2.5. Dados de frete (vindos do frontend - serão RECALCULADOS no backend)
    shipping_service_id = data.get('shipping_service_id')
    shipping_cep = data.get('shipping_cep', '')
    
    # 2.6. Dados de endereço de entrega
    shipping_address_data = data.get('shipping_address', {})
    shipping_addr = shipping_address_data.get('address', '')
    shipping_number = shipping_address_data.get('number', '')
    shipping_complement = shipping_address_data.get('complement', '')
    shipping_neighborhood = shipping_address_data.get('neighborhood', '')
    shipping_city = shipping_address_data.get('city', '')
    shipping_state = shipping_address_data.get('state', '')
    customer_cpf = data.get('customer_cpf', '')
    customer_phone = data.get('customer_phone', '')
    
    # O Mercado Pago Brick envia o objeto payer completo dentro de formData
    payer_data = data.get('payer', {})
    
    # 1. Email (Obrigatório)
    payer_email = payer_data.get("email")
    if not payer_email:
        payer_email = user.email if user and user.email else "fake@domain.com"

    # Constrói o objeto payer final
    payer = {
        "email": payer_email,
        "entity_type": "individual", # Exigido pelo MP para transações com CPF
        "first_name": payer_data.get("first_name") or (user.name.split()[0] if hasattr(user, 'name') and user.name else "Cliente"),
        "last_name": payer_data.get("last_name") or "Rocca"
    }
    
    # 2. Identificação (CPF/CNPJ) - Mantém exatamente o que o frontend enviou
    if payer_data.get("identification") and payer_data["identification"].get("number"):
        payer["identification"] = payer_data["identification"]

    total_order = sum(item.price * item.quantity for item in cart.cart_items)

    # 3. Verifica estoque antes de processar e cria array para validar cupom
    cart_items_data = []
    for item in cart.cart_items:
        variant = ProductVariant.query.get(item.product_variant_id)
        if not variant or variant.stock < item.quantity:
            return jsonify({'message': f'Estoque insuficiente para {variant.size} do produto {variant.product.name}'}), 400
            
        cart_items_data.append({
             'product_id': item.product_id,
             'variant_id': item.product_variant_id,
             'price': float(item.price),
             'quantity': item.quantity
        })

    # 3.5. Validação de Cupom
    discount_amount = 0.0
    applied_coupon_id = None
    free_shipping_coupon = False
    
    if coupon_code:
        # Importa a função de validação pública
        from .public_coupon_routes import check_coupon_validity, Coupon
        
        # Faz uma chamada simulando a lógica da rota /validate
        validity = check_coupon_validity(coupon_code, float(total_order), user_id=user_id)
        if validity.get('valid'):
             coupon = validity.get('coupon')
             # Re-avalia itens elegíveis
             eligible_total = 0.0
             has_any_eligible = False
             
             included_products = [pc.product_id for pc in coupon.product_coupons if not pc.excluir]
             excluded_products = [pc.product_id for pc in coupon.product_coupons if pc.excluir]
             included_categories = [cc.category_id for cc in coupon.category_coupons if not cc.excluir]
             excluded_categories = [cc.category_id for cc in coupon.category_coupons if cc.excluir]
             included_collections = [cc.collection_id for cc in coupon.collection_coupons if not cc.excluir]
             excluded_collections = [cc.collection_id for cc in coupon.collection_coupons if cc.excluir]
             
             for item in cart.cart_items:
                 p = item.product
                 subtotal = float(item.price * item.quantity)
                 is_eligible = True
                 
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
                          
                 if not is_eligible: continue
                 
                 needed_inclusion = False
                 included = False
                 if coupon.produtos:
                     needed_inclusion = True
                     if p.id in included_products: included = True
                 if coupon.categorias:
                     needed_inclusion = True
                     p_cats = [pc.category_id for pc in p.product_categories]
                     if any(c in included_categories for c in p_cats): included = True
                 if coupon.colecoes:
                     needed_inclusion = True
                     p_cols = [pc.collection_id for pc in p.product_collections]
                     if any(c in included_collections for c in p_cols): included = True
                     
                 if needed_inclusion and not included:
                     is_eligible = False
                     
                 if is_eligible:
                      eligible_total += subtotal
                      has_any_eligible = True
                      
             if has_any_eligible:
                 base_calc = eligible_total if coupon.excluir_item_com_desconto else float(total_order)
                 
                 if coupon.porcentagem:
                     discount_amount = base_calc * (float(coupon.valor) / 100.0)
                 else:
                     discount_amount = min(float(coupon.valor), base_calc)
                     
                 applied_coupon_id = coupon.id
                 total_order = float(total_order) - discount_amount
                 
                 # Verifica se é cupom de frete grátis
                 if coupon.frete_gratis:
                     free_shipping_coupon = True
                 
                 # Incrementa o uso do cupom se aprovado (nós salvamos o order e o decremento depois)
        else:
            return jsonify({"message": validity.get('message', 'Cupom inválido.')}), 400

    # 4. RECÁLCULO DE FRETE NO BACKEND (nunca confiar no frontend)
    shipping_price = 0.0
    shipping_service_name = None
    shipping_delivery_time = None
    is_pickup_order = str(shipping_service_id) == 'pickup'
    
    if is_pickup_order:
        # Retirada: frete zero, sem recalcular na API
        # shipping_service_id deve ser None (coluna INT no banco — não pode salvar string 'pickup')
        shipping_service_id = None
        shipping_price = 0.0
        shipping_service_name = 'Retirada'
        shipping_delivery_time = None
        print("[CHECKOUT] Pedido de Retirada — frete zerado.")
    elif shipping_service_id and shipping_cep:
        # Se o cupom é de frete grátis, zera imediatamente — sem recalcular
        if free_shipping_coupon:
            # Ainda precisamos do nome/tempo do serviço para registrar no pedido
            shipping_service_name = "Frete Grátis"
            shipping_delivery_time = None
            shipping_price = 0.0
            print(f"[CHECKOUT] Cupom de frete grátis aplicado — frete zerado.")
        else:
            from ..services.melhor_envio_service import MelhorEnvioService, MelhorEnvioError
            from ..models import Product
            
            try:
                # Monta produtos reais do banco
                shipping_products = []
                for item in cart.cart_items:
                    product = Product.query.get(item.product_id)
                    if product:
                        shipping_products.append({
                            "weight": float(product.weight),
                            "width": float(product.dimensionL),
                            "height": float(product.dimensionA),
                            "length": float(product.dimensionC),
                            "quantity": item.quantity,
                        })
                
                # Recalcula frete com dados REAIS do backend
                service = MelhorEnvioService()
                options = service.calculate_shipping(shipping_cep, shipping_products)
                
                # Encontra a opção selecionada pelo ID
                selected = None
                for opt in options:
                    if opt["id"] == shipping_service_id:
                        selected = opt
                        break
                
                if not selected:
                    return jsonify({"message": "Serviço de frete selecionado não está disponível para este CEP."}), 400
                
                shipping_price = selected["price"]
                shipping_service_name = selected["name"]
                shipping_delivery_time = selected["delivery_time"]
                
                # Soma o frete ao total do pedido
                total_order = float(total_order) + shipping_price
                
                print(f"[CHECKOUT] Frete recalculado: {shipping_service_name} = R${shipping_price:.2f} ({shipping_delivery_time} dias)")
                
            except MelhorEnvioError as e:
                print(f"[CHECKOUT] Erro ao recalcular frete: {e}")
                return jsonify({"message": f"Erro no cálculo de frete: {str(e)}"}), e.status_code or 500
                 
                 
    print(f"DEBUG CHECKOUT: user_id={user_id}, total={total_order}, coupon_id={applied_coupon_id}, frete={shipping_price}")
    new_order_id = generate_order_id()  # Gera ID alfanumérico único ANTES do objeto (ex: '4821RK')
    order = Order(
        id=new_order_id,
        user_id=user_id, 
        status='pending',
        payment_status='pending',
        payment_method=payment_method_id,
        installments=installments,
        total=total_order,
        coupon_id=applied_coupon_id,
        discount_amount=discount_amount,
        is_paid=False,
        shipping_price=shipping_price,
        shipping_service_name=shipping_service_name,
        shipping_service_id=shipping_service_id,
        shipping_delivery_time=shipping_delivery_time,
        shipping_cep=shipping_cep,
        shipping_address=shipping_addr,
        shipping_number=shipping_number,
        shipping_complement=shipping_complement,
        shipping_neighborhood=shipping_neighborhood,
        shipping_city=shipping_city,
        shipping_state=shipping_state,
        customer_cpf=customer_cpf,
    )
    db.session.add(order)
    db.session.flush()  # Confirma o INSERT com o id já definido
    print(f"DEBUG CHECKOUT: order.id={order.id} created with coupon_id={order.coupon_id}")

    # Salvar telefone no cadastro do usuário (para próximas compras)
    if customer_phone and user and not user.phone:
        user.phone = customer_phone

    # 5. Transfere os itens do carrinho pro pedido
    for item in cart.cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            product_variant_id=item.product_variant_id,
            quantity=item.quantity,
            price=item.price
        )
        db.session.add(order_item)

    # 6. Processamento do Pagamento Mercado Pago
    mp_access_token = os.environ.get("MP_ACCESS_TOKEN")
    if not mp_access_token:
        # Se não configurou, apenas simula sucesso local (fallback de dev)
        order.status = 'paid'
        order.payment_status = 'approved'
        order.is_paid = True
        for order_item in order.order_items:
            var = ProductVariant.query.get(order_item.product_variant_id)
            var.stock -= order_item.quantity
            
        if order.coupon_id:
            from .public_coupon_routes import Coupon
            c = Coupon.query.get(order.coupon_id)
            if c:
                c.vezes_usado += 1
        
        for item in cart.cart_items:
            db.session.delete(item)
        db.session.delete(cart)
        db.session.commit()
        # Enviar e-mail de confirmaçao de pedido (dev mode)
        try:
            from .user_routes import send_order_confirmation_email
            send_order_confirmation_email(order, user)
        except Exception as email_err:
            print(f"[EMAIL] Erro ao enviar confirmação (dev): {email_err}")
        return jsonify({'message': 'Dev mode: Pedido finalizado.', 'order_id': order.id, 'status': 'approved'}), 201

    sdk = mercadopago.SDK(mp_access_token)

    payment_data = {
        "transaction_amount": float(total_order),
        "description": f"Pedido #{order.id} Rocca",
        "payment_method_id": payment_method_id,
        "payer": payer,
        "external_reference": str(order.id)
    }

    if token:
         payment_data["token"] = token
         payment_data["installments"] = installments
         
    if issuer_id:
         payment_data["issuer_id"] = issuer_id
         
    # Não logar dados sensíveis (token do cartão, payer, CPF) em produção
         
    # Importante: para PIX, payer.email e payer.first_name são importantes
    
    payment_response = sdk.payment().create(payment_data)
    payment = payment_response.get("response", {})

    if payment.get("error") or payment.get("status") == "rejected":
         db.session.rollback()
         return jsonify({"message": "Pagamento recusado.", "details": {"status": payment.get("status"), "status_detail": payment.get("status_detail")}}), 400

    order.payment_id = str(payment.get("id"))
    order.payment_status = payment.get("status")

    if order.payment_status == 'approved':
        order.is_paid = True
        order.status = 'paid'
        for order_item in order.order_items:
            variant = ProductVariant.query.get(order_item.product_variant_id)
            variant.stock -= order_item.quantity

    # Limpa o carrinho
    for item in cart.cart_items:
        db.session.delete(item)
        
    # Incrementa uso cupom com aprovação
    if order.payment_status == 'approved' and applied_coupon_id:
        from .public_coupon_routes import Coupon
        coupon = Coupon.query.get(applied_coupon_id)
        if coupon:
            coupon.vezes_usado += 1
            
    db.session.delete(cart)

    db.session.commit()

    # Enviar e-mail de confirmaçao se pagamento aprovado
    if order.payment_status == 'approved':
        try:
            from .user_routes import send_order_confirmation_email
            send_order_confirmation_email(order, user)
        except Exception as email_err:
            print(f"[EMAIL] Erro ao enviar confirmação (MP): {email_err}")

    return jsonify({
        'message': 'Pedido processado.', 
        'order_id': order.id,
        'status': order.payment_status,
        'payment_data': {
            'status': payment.get('status'),
            'status_detail': payment.get('status_detail'),
            'point_of_interaction': payment.get('point_of_interaction'),  # para PIX QR Code
        }
    }), 201

#################################################################################


################################### Limpar Carrinho ####################################
@user_cart_routes.route('/cart/clear', methods=['DELETE'])
@jwt_required()
@limiter.limit("20 per minute")
def limpar_carrinho():
    user_id = get_jwt_identity()

    pedido_aberto = Cart.query.filter_by(user_id=user_id, is_active=True).first()
    if not pedido_aberto:
        return jsonify({'mensagem': 'Carrinho já está vazio'}), 200

    CartItem.query.filter_by(cart_id=pedido_aberto.id).delete()
    Cart.query.filter_by(id=pedido_aberto.id).delete()
    db.session.commit()

    return jsonify({'mensagem': 'Carrinho limpo com sucesso'}), 200
#########################################################################################


############################## Remover Item do Carrinho ##################################
@user_cart_routes.route('/cart/remove', methods=['DELETE'])
@jwt_required()
@limiter.limit("30 per minute")
def remover_item_carrinho():
    user_id = get_jwt_identity()
    data = request.get_json()
    product_id = data.get('product_id')
    size = data.get('size')

    if not product_id or not size:
        return jsonify({'error': 'Produto e tamanho são obrigatórios.'}), 400

    cart = Cart.query.filter_by(user_id=user_id, is_active=True).first()
    if not cart:
        return jsonify({'error': 'Carrinho não encontrado.'}), 404

    variant = ProductVariant.query.filter_by(product_id=product_id, size=size).first()
    if not variant:
        return jsonify({'error': 'Variante não encontrada.'}), 404

    item = CartItem.query.filter_by(
        cart_id=cart.id,
        product_id=product_id,
        product_variant_id=variant.product_variant_id
    ).first()

    if not item:
        return jsonify({'error': 'Item não encontrado no carrinho.'}), 404

    db.session.delete(item)
    db.session.flush()  # Garante que o item seja marcado como removido antes da verificação

    remaining_items = CartItem.query.filter_by(cart_id=cart.id).count()

    if remaining_items == 0:
        db.session.delete(cart)
    else:
        cart.total = calculate_cart_total(cart)
    db.session.commit()

    return jsonify({'message': 'Item removido do carrinho com sucesso.'}), 200
##########################################################################################


################################### Mesclar Carrinho #####################################
@user_cart_routes.route('/cart/merge', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def merge_cart():
    user_id = get_jwt_identity()
    data = request.get_json()
    guest_items = data.get('items', [])

    if not guest_items:
        return jsonify({'message': 'Nenhum item para mesclar.'}), 200

    # 1. Busca ou cria o carrinho do usuário
    cart = Cart.query.filter_by(user_id=user_id, is_active=True).first()
    if not cart:
        cart = Cart(user_id=user_id, is_active=True)
        db.session.add(cart)
        db.session.commit() # Commit para ter o ID do carrinho

    # 2. Itera sobre os itens do visitante e adiciona/atualiza no carrinho do usuário
    for item in guest_items:
        product_id = item.get('product_id')
        variant_id = item.get('variant_id') # ID da variante é crucial
        quantity = item.get('quantity', 1)

        if not product_id or not variant_id:
            continue

        # Verifica estoque (opcional, mas recomendado)
        variant = ProductVariant.query.get(variant_id)
        if not variant:
            continue # Pula se variante não existir (ex: produto deletado)

        # Verifica se item já existe no carrinho do usuário
        cart_item = CartItem.query.filter_by(
            cart_id=cart.id,
            product_variant_id=variant_id
        ).first()

        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=product_id, # Redundante mas mantido na modelagem atual
                product_variant_id=variant_id,
                quantity=quantity,
                price=variant.product.price # Preço atual do produto
            )
            db.session.add(cart_item)

    # 3. Recalcula total e salva
    db.session.commit() # Commit dos itens para garantir que estão salvos antes do cálculo (se depender do banco)
    
    # Recalcula total usando a função helper se ela considerar itens no banco, 
    # ou recalcula iterando
    cart.total = calculate_cart_total(cart)
    db.session.commit()

    return jsonify({'message': 'Carrinho mesclado com sucesso.'}), 200
##########################################################################################


################################### Atualizar Quantidade #################################
@user_cart_routes.route('/cart/update', methods=['PUT'])
@jwt_required()
@limiter.limit("30 per minute")
def update_cart_quantity():
    user_id = get_jwt_identity()
    data = request.get_json()
    product_id = data.get('product_id')
    size = data.get('size')
    quantity = data.get('quantity')

    if not product_id or not size or quantity is None or quantity < 1:
        return jsonify({'error': 'Dados inválidos.'}), 400

    cart = Cart.query.filter_by(user_id=user_id, is_active=True).first()
    if not cart:
        return jsonify({'error': 'Carrinho não encontrado.'}), 404

    variant = ProductVariant.query.filter_by(product_id=product_id, size=size).first()
    if not variant:
        return jsonify({'error': 'Variante não encontrada.'}), 404

    item = CartItem.query.filter_by(
        cart_id=cart.id,
        product_variant_id=variant.product_variant_id
    ).first()

    if not item:
        return jsonify({'error': 'Item não encontrado no carrinho.'}), 404

    # Atualiza quantidade
    # Opcional: Verificar estoque novamente (variant.stock < quantity)
    if variant.stock < quantity:
         return jsonify({'error': 'Estoque insuficiente para essa quantidade.'}), 400

    item.quantity = quantity
    
    # Recalcula total
    db.session.commit() # Salva item
    cart.total = calculate_cart_total(cart)
    db.session.commit() # Salva total

    return jsonify({'message': 'Quantidade atualizada.'}), 200
##########################################################################################