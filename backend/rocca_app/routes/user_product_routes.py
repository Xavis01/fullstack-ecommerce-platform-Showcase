# backend/rocca_app/routes/user_products_routes.py

from flask import Blueprint, jsonify
from ..models import Product, ProductImage, ProductCategory
from sqlalchemy.orm import joinedload


user_product_routes = Blueprint('user_product_routes', __name__)


def _is_coming_soon(product):
    """Retorna True se o produto tiver a categoria 'EM BREVE'."""
    return any(cat.name.upper() == 'EM BREVE' for cat in product.categories)


def _get_cover_data(product):
    """Retorna os dados da imagem de capa (image_url, thumbnail_url, placeholder_blur)."""
    cover_image = next((img for img in product.images if img.is_cover), None)
    if not cover_image and product.images:
        cover_image = product.images[0]
    
    if cover_image:
        return {
            "image_url": cover_image.image_public_url,
            "thumbnail_url": cover_image.thumbnail_public_url or cover_image.image_public_url,
            "placeholder_blur": cover_image.placeholder_blur
        }
    
    return {
        "image_url": product.image_url,
        "thumbnail_url": product.image_url,
        "placeholder_blur": None
    }


def _serialize_images(images):
    """Serializa a lista de imagens de um produto incluindo thumbnails."""
    return [{
        'id': img.id,
        'url': img.image_public_url,
        'thumbnail_url': img.thumbnail_public_url or img.image_public_url,
        'is_cover': img.is_cover
    } for img in images]


###################################### Listar Produtos ###########################################
@user_product_routes.route('/products/list', methods=['GET'])
def list_products():

    products = Product.query.options(
        joinedload(Product.variants),
        joinedload(Product.images),
        joinedload(Product.categories)
    ).filter_by(is_public=True, is_active=True).order_by(Product.sort_order.asc(), Product.id.asc()).all()

    output = []
    for product in products:
        variants = [
            {"id": variant.product_variant_id, "size": variant.size, "stock": variant.stock}
            for variant in product.variants
        ]

        cover_data = _get_cover_data(product)
        coming_soon = _is_coming_soon(product)

        output.append({
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "collection": product.collection,
            "price": float(product.price),
            "image_url": cover_data["image_url"],
            "thumbnail_url": cover_data["thumbnail_url"],
            "placeholder_blur": cover_data["placeholder_blur"],
            "images": _serialize_images(product.images),
            "variants": variants,
            "is_coming_soon": coming_soon
        })
    return jsonify(output)
###################################################################################################


############################## Produto especifico ###################################
@user_product_routes.route('/products/list/<int:product_id>', methods=['GET'])
def get_product(product_id):

    product = Product.query.options(
        joinedload(Product.variants),
        joinedload(Product.images),
        joinedload(Product.categories)
    ).get(product_id)

    if not product or not product.is_active:
        return jsonify({'error': 'Produto não encontrado'}), 404

    # Bloqueia acesso a produtos "EM BREVE"
    if _is_coming_soon(product):
        return jsonify({'error': 'Produto não disponível'}), 403

    cover_data = _get_cover_data(product)

    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'collection': product.collection,
        'price': float(product.price),
        'image_url': cover_data["image_url"],
        'thumbnail_url': cover_data["thumbnail_url"],
        'placeholder_blur': cover_data["placeholder_blur"],
        'images': _serialize_images(product.images),
        'variants': [
            {
                'id': variant.product_variant_id,
                'size': variant.size,
                'stock': variant.stock
            } for variant in product.variants
        ],
        'is_coming_soon': False
    })


############################## Produtos em Destaque ###################################
@user_product_routes.route('/products/highlights', methods=['GET'])
def get_highlights():
    from ..models import Category

    # Busca a categoria "DESTAQUE"
    category = Category.query.filter(Category.name.ilike('DESTAQUE')).first()

    if not category:
        return jsonify([])

    # Busca até 6 produtos dessa categoria que sejam públicos e ativos, ordenados por highlight_order
    products = Product.query.join(ProductCategory).filter(
        ProductCategory.category_id == category.id,
        Product.is_public == True,
        Product.is_active == True
    ).options(
        joinedload(Product.variants),
        joinedload(Product.images),
        joinedload(Product.categories)
    ).order_by(ProductCategory.highlight_order.asc(), Product.id.asc()).limit(6).all()

    output = []
    for product in products:
        variants = [
            {"id": variant.product_variant_id, "size": variant.size, "stock": variant.stock}
            for variant in product.variants
        ]

        coming_soon = _is_coming_soon(product)

        # Destaques usam a ÚLTIMA imagem (conforme decisão de design)
        last_image = product.images[-1] if product.images else None
        image_url = last_image.image_public_url if last_image else product.image_url
        thumbnail_url = (last_image.thumbnail_public_url or last_image.image_public_url) if last_image else product.image_url
        placeholder_blur = last_image.placeholder_blur if last_image else None

        output.append({
            "id": product.id,
            "name": product.name,
            "price": float(product.price),
            "image_url": image_url,
            "thumbnail_url": thumbnail_url,
            "placeholder_blur": placeholder_blur,
            "images": _serialize_images(product.images),
            "variants": variants,
            "is_coming_soon": coming_soon
        })

    return jsonify(output)
######################################################################################

############################## Media do Archive ###################################
@user_product_routes.route('/archive-media', methods=['GET'])
def get_archive_media():
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(current_dir, '..', '..', '..')
    target_dir = os.path.normpath(os.path.join(project_root, 'frontend', 'public', 'bentoGridArquive'))

    try:
        files = os.listdir(target_dir)
        valid_exts = {'.jpg', '.jpeg', '.heic', '.mov', '.mp4', '.webp'}
        media_files = [f for f in files if os.path.splitext(f)[1].lower() in valid_exts and f != 'manifest.json']
        return jsonify(media_files)
    except Exception as e:
        return jsonify([])

@user_product_routes.route('/archive-manifest', methods=['GET'])
def get_archive_manifest():
    import os, json
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(current_dir, '..', '..', '..')
    manifest_path = os.path.normpath(os.path.join(project_root, 'frontend', 'public', 'bentoGridArquive', 'manifest.json'))

    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except Exception:
        return jsonify({})
######################################################################################