# backend/rocca_app/routes/admin_product_routes.py

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..models import db, Product, User, ProductVariant, Order, OrderItem, ProductCategory, Category, CartItem, ProductImage, Collection, ProductCollection
from ..utils.upload_utils import save_image, delete_remote_image
import secrets
from ..routes.admin_routes import admin_required

admin_product_routes = Blueprint('admin_product_routes', __name__)
flask_env = os.getenv("FLASK_ENV", "development")


############################# Utils pra deletar todas imagens de um produto ####################################
def delete_all_product_images_util(product_id):
    """
    Deleta todas as imagens de um produto (físicas e do banco)
    Retorna True se bem sucedido, False com mensagem de erro caso contrário
    """
    try:
        images = ProductImage.query.filter_by(product_id=product_id).all()
        if not images:
            return True, "Nenhuma imagem encontrada"
        
        for image in images:
            try:
                delete_remote_image(image.image_url)
            except Exception as e:
                # Registra erro mas continua processo
                current_app.logger.error(f"Erro deletando imagem {image.id}: {str(e)}")
            db.session.delete(image)
        
        return True, f"{len(images)} imagens deletadas"
    
    except Exception as e:
        return False, f"Erro geral: {str(e)}"

# #################################################################################################################


################# Cadastrar Produtos ############################################
@admin_product_routes.route('/admin/products/create', methods=['POST'])
@jwt_required()
@admin_required
def create_product():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    category_ids = data.get('category_ids', [])  # Espera uma lista de IDs de categorias, ou uma lista vazia
    categories = []

    if category_ids:  # Se houver categoria_ids fornecidos, tenta buscar as categorias
        categories = Category.query.filter(Category.id.in_(category_ids)).all()

        if not categories:
            return jsonify({'error': 'Uma ou mais categorias não encontradas'}), 400

    collection_ids = data.get('collection_ids', [])
    collections = []
    if collection_ids:
        collections = Collection.query.filter(Collection.id.in_(collection_ids)).all()
        if not collections:
            return jsonify({'error': 'Uma ou mais coleções não encontradas'}), 400

    price = data.get('price')
    # Novos campos de envio
    weight = data.get('weight', 0.00)
    dimensionC = data.get('dimensionC', 0.00)
    dimensionL = data.get('dimensionL', 0.00)
    dimensionA = data.get('dimensionA', 0.00)

    is_public = data.get('is_public', True)
    is_active = data.get('is_active', True)
    variants_data = data.get('variants', [])

    product = Product(
        name=name,
        description=description,
        collection=collections[0].name if collections else None,
        price=price,
        weight=weight,
        dimensionC=dimensionC,
        dimensionL=dimensionL,
        dimensionA=dimensionA,
        is_public=is_public,
        is_active=is_active)

    # Se categorias foram fornecidas, associamos ao produto
    db.session.add(product)
    db.session.flush()  # Garante que o ID do produto já existe

    # Cria ligações em ProductCategory com nome da categoria e nome do produto
    for category in categories:
        pc = ProductCategory(
            product_id=product.id,
            category_id=category.id,
            category_name=category.name,
            product_name=product.name  # ou outro valor fixo que quiser associar
        )
        db.session.add(pc)

    for col in collections:
        pcol = ProductCollection(
            product_id=product.id,
            collection_id=col.id,
            product_name=product.name,
            collection_name=col.name
        )
        db.session.add(pcol)

    db.session.add(product)
    db.session.flush()  # Garante que o ID do produto já existe

    total_stock = 0
    for variant in variants_data:
        size = variant.get('size')
        stock = variant.get('stock', 0)
        total_stock += stock
        pv = ProductVariant(product_id=product.id, size=size, stock=stock)
        db.session.add(pv)

    db.session.commit()

    return jsonify({'message': 'Produto criado com sucesso', 'product_id': product.id}), 201

####################################################################################


########################## Atualizar Produtos ####################################
@admin_product_routes.route('/admin/products/update/<int:product_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Produto não encontrado'}), 404

    data = request.get_json()

    # Atualiza os campos básicos
    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.collection = data.get('collection', product.collection)
    product.price = data.get('price', product.price)
    
    # Atualiza novos campos de envio
    product.weight = data.get('weight', product.weight)
    product.dimensionC = data.get('dimensionC', product.dimensionC)
    product.dimensionL = data.get('dimensionL', product.dimensionL)
    product.dimensionA = data.get('dimensionA', product.dimensionA)

    # Atualiza categorias, se fornecidas
    category_ids = data.get('category_ids')
    if category_ids is not None:
        # Remove associações existentes
        ProductCategory.query.filter_by(product_id=product.id).delete()
        if category_ids:
            categories = Category.query.filter(Category.id.in_(category_ids)).all()
            if len(categories) != len(category_ids):
                return jsonify({'error': 'Uma ou mais categorias não encontradas'}), 400
            for category in categories:
                pc = ProductCategory(
                    product_id=product.id,
                    category_id=category.id,
                    category_name=category.name,
                    product_name=product.name
                )
                db.session.add(pc)

    collection_ids = data.get('collection_ids')
    if collection_ids is not None:
        ProductCollection.query.filter_by(product_id=product.id).delete()
        if collection_ids:
            collections_list = Collection.query.filter(Collection.id.in_(collection_ids)).all()
            for col in collections_list:
                pcol = ProductCollection(
                    product_id=product.id,
                    collection_id=col.id,
                    product_name=product.name,
                    collection_name=col.name
                )
                db.session.add(pcol)
            if collections_list:
                product.collection = collections_list[0].name
            else:
                product.collection = None

    # --- LÓGICA CORRIGIDA DAS VARIANTES ---
    variants_data = data.get('variants', [])

    # Cria um set dos valores (size) enviados do frontend
    sent_sizes = set([v['size'] for v in variants_data if v.get('size')])

    # Busca todas variantes atualmente no banco
    db_variants = {v.size: v for v in product.variants}

    # REMOVE variantes que não estão mais na lista enviada
    for size, variant_obj in list(db_variants.items()):
        if size not in sent_sizes:
            db.session.delete(variant_obj)

    # Atualiza ou adiciona variantes da lista recebida
    for variant_data in variants_data:
        size = variant_data.get('size')
        stock = variant_data.get('stock', 0)
        if size in db_variants:
            db_variants[size].stock = stock
        else:
            db.session.add(ProductVariant(product_id=product.id, size=size, stock=stock))

    db.session.commit()

    return jsonify({'message': 'Produto atualizado com sucesso'}), 200


###################################################################################


####################### Soft Delete de Produto ####################################
@admin_product_routes.route('/admin/products/delete/<int:product_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def soft_delete_product(product_id):
    product = Product.query.get(product_id)

    if not product:
        return jsonify({'error': 'Produto não encontrado'}), 404

    if not product.is_active:
        return jsonify({'error': 'Produto já está inativo'}), 400

    product.is_active = False
    product.is_public = False
    db.session.commit()

    return jsonify({'message': 'Produto desativado com sucesso'}), 200
#####################################################################################


################################## Soft Delete Multiplo ##########################################
@admin_product_routes.route('/admin/products/delete-multiple', methods=['DELETE'])
@jwt_required()
@admin_required
def soft_delete_multiple_products():
    data = request.get_json()

    if not data or 'product_ids' not in data:
        return jsonify({'error': 'É necessário enviar uma lista de product_ids'}), 400

    product_ids = data['product_ids']
    
    if not isinstance(product_ids, list) or not all(isinstance(pid, int) for pid in product_ids):
        return jsonify({'error': 'product_ids deve ser uma lista de inteiros'}), 400

    desativados = []
    ignorados = []

    for product_id in product_ids:
        product = Product.query.get(product_id)

        if not product or not product.is_active:
            ignorados.append(product_id)
            continue

        product.is_active = False
        product.is_public = False
        desativados.append(product_id)

    db.session.commit()

    return jsonify({
        'message': 'Processo concluído',
        'desativados': desativados,
        'ignorados': ignorados
    }), 200
######################################################################################################


################################# Hard Delete de Produto ####################################
@admin_product_routes.route('/admin/products/hard-delete/<int:product_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def hard_delete_product(product_id):
    product = Product.query.get(product_id)

    if not product:
        return jsonify({'error': 'Produto não encontrado'}), 404

    if product.is_active:
        return jsonify({'error': 'Produto ainda está ativo. Faça soft delete antes'}), 400

    if product.order_items:
        return jsonify({'error': 'Produto já foi comprado e não pode ser deletado'}), 400

    # Deletar todas as imagens primeiro
    success, msg = delete_all_product_images_util(product_id)
    if not success:
        return jsonify({'error': f'Falha ao deletar imagens: {msg}'}), 500

    # Agora deletar o produto
    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Produto e imagens deletados permanentemente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao deletar produto: {str(e)}'}), 500
#############################################################################################


############################################ Hard Delete Multiplo ###########################################
@admin_product_routes.route('/admin/products/hard-delete-multiple', methods=['DELETE'])
@jwt_required()
@admin_required
def hard_delete_multiple_products():
    data = request.get_json()
    if not data or 'product_ids' not in data:
        return jsonify({'error': 'É necessário enviar uma lista de product_ids'}), 400

    product_ids = data['product_ids']
    deletados = []
    ignorados = []

    for product_id in product_ids:
        product = Product.query.get(product_id)
        
        if not product:
            ignorados.append({'id': product_id, 'motivo': 'Produto não encontrado'})
            continue
            
        if product.is_active:
            ignorados.append({'id': product_id, 'motivo': 'Produto ainda está ativo'})
            continue
            
        if product.order_items:
            ignorados.append({'id': product_id, 'motivo': 'Produto já foi comprado'})
            continue
            
        # Deletar imagens primeiro
        success, _ = delete_all_product_images_util(product_id)
        if not success:
            ignorados.append({'id': product_id, 'motivo': 'Falha ao deletar imagens'})
            continue
            
        # Deletar produto
        try:
            db.session.delete(product)
            deletados.append(product_id)
        except Exception as e:
            ignorados.append({'id': product_id, 'motivo': f'Erro ao deletar: {str(e)}'})
            
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro no commit final: {str(e)}'}), 500

    return jsonify({
        'message': 'Processo concluído',
        'deletados': deletados,
        'ignorados': ignorados
    }), 200

#################################################################################################################


############################ Hard Delet de TODOS os Produtos ##############################
@admin_product_routes.route('/admin/products/hard-delete-all', methods=['DELETE'])
@jwt_required()
@admin_required
def hard_delete_all_inactive_products():
    products_with_order_items = db.session.query(OrderItem.product_id).distinct()
    variants_with_cart_items = db.session.query(ProductVariant.product_id).join(CartItem).distinct()

    products_to_delete = Product.query.filter(
        Product.is_active == False,
        ~Product.id.in_(products_with_order_items),
        ~Product.id.in_(variants_with_cart_items)
    ).all()

    deleted_count = 0
    errors = []

    for product in products_to_delete:
        # Deletar imagens primeiro
        success, img_msg = delete_all_product_images_util(product.id)
        if not success:
            errors.append(f"Produto {product.id}: {img_msg}")
            continue
            
        # Deletar produto
        try:
            db.session.delete(product)
            deleted_count += 1
        except Exception as e:
            errors.append(f"Produto {product.id}: {str(e)}")
            
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro no commit final: {str(e)}'}), 500

    response = {
        'message': f'{deleted_count} produtos deletados',
        'deleted_count': deleted_count
    }
    
    if errors:
        response['errors'] = errors
        return jsonify(response), 207
        
    return jsonify(response), 200
#########################################################################################



########################### Restore de Produto ####################################
@admin_product_routes.route('/admin/products/restore/<int:product_id>', methods=['PUT'])
@jwt_required()
@admin_required
def restore_product(product_id):
    product = Product.query.get(product_id)

    if not product:
        return jsonify({'error': 'Produto não encontrado'}), 404

    if product.is_active:
        return jsonify({'error': 'Produto já está ativo'}), 400

    product.is_active = True
    db.session.commit()

    return jsonify({'message': 'Produto desativado com sucesso'}), 200
#####################################################################################


############################## Restore de Todos os Produtos ###########################################
@admin_product_routes.route('/admin/products/restore-all', methods=['PUT'])
@jwt_required()
@admin_required
def restore_all_product():
    products_to_restore = Product.query.filter(Product.is_active == False).all()

    for product in products_to_restore:
        product.is_active = True

    db.session.commit()

    return jsonify({
        'message': 'Todos os produtos foram restaurados com sucesso!.'
    }), 200


########################### Atualizar Preços Rápidos (Bulk) ###########################
@admin_product_routes.route('/admin/products/fast-prices/bulk-update', methods=['PUT'])
@jwt_required()
@admin_required
def bulk_update_fast_prices():
    data = request.get_json()
    updates = data.get('updates', []) # Lista de {id: 1, fast_price: 10.0}

    if not updates:
        return jsonify({'message': 'Nenhuma alteração enviada'}), 200

    try:
        count = 0
        for update in updates:
            product_id = update.get('id')
            new_price = update.get('fast_price')
            
            if product_id is not None and new_price is not None:
                product = Product.query.get(product_id)
                if product:
                    product.fast_price = new_price
                    count += 1
        
        db.session.commit()
        return jsonify({'message': f'{count} preços atualizados com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
#######################################################################################


###################################### Listar todos Produtos #########################################
@admin_product_routes.route('/admin/products/list', methods=['GET'])
@jwt_required()
@admin_required
def list_products():
    from sqlalchemy.orm import joinedload
    
    status = request.args.get('status', 'ativo')

    query = Product.query.options(
        joinedload(Product.variants),
        joinedload(Product.images),
        joinedload(Product.product_categories),
        joinedload(Product.product_collections)
    )

    if status == 'ativo':
        products = query.filter_by(is_active=True).all()
    elif status == 'inativo':
        products = query.filter_by(is_active=False).all()
    else:
        products = query.all()

    output = []
    for product in products:
        # Pegando as variantes do produto (já carregadas)
        variants = [
            {"id": variant.product_variant_id, "size": variant.size, "stock": variant.stock}
            for variant in product.variants
        ]

        # Filtrando imagens de capa em Python (já carregadas)
        cover_images_list = [
            {
                "id": img.id,
                "image_public_url": img.image_public_url,
                "is_cover": img.is_cover
            }
            for img in product.images if img.is_cover
        ]
        
        # Lista de IDs de categorias
        category_ids = [pc.category_id for pc in product.product_categories]
        collection_ids = [pc.collection_id for pc in product.product_collections]
        
        # Fallback se não tiver capa, pega a primeira
        first_image_url = None
        if cover_images_list:
            first_image_url = cover_images_list[0]['image_public_url'] # Use public url if available
        elif product.images:
             first_image_url = product.images[0].image_url

        output.append({
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "collection": product.collection,
            "price": float(product.price),
            "price": float(product.price),
            "fast_price": float(product.fast_price) if product.fast_price is not None else float(product.price),
            "weight": float(product.weight),
            "dimensionC": float(product.dimensionC),
            "dimensionL": float(product.dimensionL),
            "dimensionA": float(product.dimensionA),
            "stock": product.stock,
            "is_public": product.is_public,
            "is_active": product.is_active,
            "category_ids": category_ids,
            "collection_ids": collection_ids,
            "variants": variants,
            "cover_images": cover_images_list,
            "image_url": first_image_url, 
            "is_scheduled": product.is_scheduled,
            "scheduled_publish_at": (product.scheduled_publish_at.isoformat() + 'Z') if product.scheduled_publish_at else None
        })
    return jsonify(output)

###################################################################################################


######################################### Listar Lixeira ############################################
@admin_product_routes.route('/admin/products/list/bin', methods=['GET'])
@jwt_required()
@admin_required
def list_bin():
    from sqlalchemy.orm import joinedload

    products = Product.query.filter_by(is_active=False).options(
        joinedload(Product.variants),
        joinedload(Product.images)
    ).all()

    order_variant_ids = {
        row[0] for row in db.session.query(OrderItem.product_variant_id).distinct().all()
    }


    cart_variant_ids = {
        row[0] for row in db.session.query(CartItem.product_variant_id).distinct().all()
    }

    output = []
    for product in products:
        variants_data = []
        variant_ids = [v.product_variant_id for v in product.variants]

        has_orders = any(vid in order_variant_ids for vid in variant_ids)
        has_cart_items = any(vid in cart_variant_ids for vid in variant_ids)

        for variant in product.variants:
            variants_data.append({
                "id": variant.product_variant_id,
                "size": variant.size,
                "stock": variant.stock
            })

        # Filtrando imagens de capa em Python (já carregadas)
        cover_images_list = [
            {
                "id": img.id,
                "image_public_url": img.image_public_url,
                "is_cover": img.is_cover
            }
            for img in product.images if img.is_cover
        ]
        
        # Fallback se não tiver capa, pega a primeira
        first_image_url = None
        if cover_images_list:
            first_image_url = cover_images_list[0]['image_public_url']
        elif product.images:
             first_image_url = product.images[0].image_url

        output.append({
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "collection": product.collection,
            "price": float(product.price),
            "stock": product.stock,
            "is_public": product.is_public,
            "is_active": product.is_active,
            "variants": variants_data,
            "cover_images": cover_images_list,
            "image_url": first_image_url,
            "has_orders": has_orders,
            "has_cart_items": has_cart_items
        })

    return jsonify(output)
###############################################################################


############################ Agendamento de Produtos ##########################
@admin_product_routes.route('/admin/products/schedule/<int:product_id>', methods=['POST'])
@jwt_required()
@admin_required
def schedule_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Produto não encontrado'}), 404

    data = request.get_json()
    scheduled_at_str = data.get('scheduled_publish_at')

    if not scheduled_at_str:
        return jsonify({'error': 'Data de agendamento obrigatória'}), 400

    try:
        from datetime import datetime, timezone
        # Frontend via .toISOString() envia UTC com 'Z' (ex: 2024-01-27T22:00:00.000Z)
        # Parse para Aware UTC
        scheduled_at_utc = datetime.fromisoformat(scheduled_at_str.replace('Z', '+00:00'))
        
        # Comparação segura (Aware vs Aware)
        if scheduled_at_utc <= datetime.now(timezone.utc):
            return jsonify({'error': 'Data de agendamento deve ser futura (verifique se a data está correta)'}), 400

        # Para salvar no banco, o scheduler agora usa UTC Naive (datetime.utcnow())
        # Então devemos converter a data recebida (que é UTC Aware) para UTC Naive
        # IMPORTANTE: Zerar segundos e microsegundos para garantir publicação no minuto exato (XX:XX:00)
        # .replace(tzinfo=None) remove o offset (+00:00) mantendo o horário UTC
        scheduled_at_utc_naive = scheduled_at_utc.replace(tzinfo=None, second=0, microsecond=0)

        product.is_scheduled = True
        product.scheduled_publish_at = scheduled_at_utc_naive
        product.is_public = False # Garante que não está público enquanto agendado
        
        db.session.commit()
        
        return jsonify({'message': 'Produto agendado com sucesso'}), 200
        
    except ValueError as e:
        return jsonify({'error': f'Formato de data inválido: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Erro interno ao agendar: {str(e)}'}), 500


@admin_product_routes.route('/admin/products/schedule/<int:product_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def cancel_schedule_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Produto não encontrado'}), 404

    product.is_scheduled = False
    product.scheduled_publish_at = None
    
    db.session.commit()
    
    return jsonify({'message': 'Agendamento cancelado com sucesso'}), 200

###############################################################################


############################ Toggle Public Status #############################
@admin_product_routes.route('/admin/products/toggle-public/<int:product_id>', methods=['PUT'])
@jwt_required()
@admin_required
def toggle_public_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Produto não encontrado'}), 404

    # Toggle
    product.is_public = not product.is_public
    
    # Se for publicado manualmente, remove o agendamento?
    # O usuário pediu "ao clicar no ícone de olho, publica ou despublica".
    # Vou remover o agendamento se for publicado manualmente para evitar conflito.
    if product.is_public:
        product.is_scheduled = False
        product.scheduled_publish_at = None

    db.session.commit()

    return jsonify({
        'message': f'Produto {"publicado" if product.is_public else "despublicado"} com sucesso',
        'is_public': product.is_public
    }), 200
###############################################################################


############################ Reordenar Destaques #############################
@admin_product_routes.route('/admin/products/highlights/reorder', methods=['PUT'])
@jwt_required()
@admin_required
def reorder_highlights():
    """
    Recebe uma lista ordenada de product_ids e atualiza highlight_order
    na tabela product_categories para a categoria DESTAQUE.
    Body: { "order": [id1, id2, id3, ...] }
    """
    data = request.get_json()
    order = data.get('order', [])

    if not order:
        return jsonify({'error': 'Lista de order é obrigatória'}), 400

    # Busca a categoria DESTAQUE
    category = Category.query.filter(Category.name.ilike('DESTAQUE')).first()
    if not category:
        return jsonify({'error': 'Categoria DESTAQUE não encontrada'}), 404

    try:
        for idx, product_id in enumerate(order):
            pc = ProductCategory.query.filter_by(
                product_id=product_id,
                category_id=category.id
            ).first()
            if pc:
                pc.highlight_order = idx
        db.session.commit()
        return jsonify({'message': 'Destaques reordenados com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
###############################################################################


############################ Reordenar Produtos da Loja #######################
@admin_product_routes.route('/admin/products/shop/reorder', methods=['PUT'])
@jwt_required()
@admin_required
def reorder_shop_products():
    """
    Recebe uma lista ordenada de product_ids e atualiza sort_order nos produtos.
    Body: { "order": [id1, id2, id3, ...] }
    """
    data = request.get_json()
    order = data.get('order', [])

    if not order:
        return jsonify({'error': 'Lista de order é obrigatória'}), 400

    try:
        for idx, product_id in enumerate(order):
            product = Product.query.get(product_id)
            if product:
                product.sort_order = idx
        db.session.commit()
        return jsonify({'message': 'Produtos reordenados com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
###############################################################################