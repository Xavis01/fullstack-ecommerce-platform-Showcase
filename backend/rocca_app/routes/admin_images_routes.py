# backend/rocca_app/routes/admin_images_routes.py

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..models import db, Product, ProductImage
from ..utils.upload_utils import save_image, delete_remote_image
import secrets
from ..routes.admin_routes import admin_required

admin_images_routes = Blueprint('admin_images_routes', __name__)
flask_env = os.getenv("FLASK_ENV", "development")
CDN_BASE_URL = os.getenv("CDN_BASE_URL", "https://example.com")


# ############################ Utils pra deletar todas imagens de um produto ####################################
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

##################################### Listar as Imagens de um produto ##################################################
@admin_images_routes.route("/admin/products/<int:product_id>/images", methods=["GET"])
@jwt_required()
@admin_required
def list_product_images(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Produto não encontrado"}), 404

    images_db = ProductImage.query.filter_by(product_id=product_id).order_by(ProductImage.id).all()
    images = [
        {"id": img.id, "image_public_url": img.image_public_url, "is_cover": img.is_cover}
        for img in images_db
    ]
    return jsonify(images), 200
#########################################################################################################################


######################################### Uploads #########################################
@admin_images_routes.route("/admin/remote-upload", methods=["POST"])
def remote_upload():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    expected_token = os.getenv("VPS_UPLOAD_TOKEN")

    if not expected_token or token != expected_token:
        return jsonify({"error": "Token de autorização inválido"}), 403

    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = request.files["file"]
    is_cover = request.form.get("is_cover", "false").lower() == "true"
    product_id = request.form.get("product_id")
    env = "dev"

    try:
        result = save_image(file, is_cover=is_cover, product_id=product_id, env=env)
        return jsonify({
            "message": "Imagem recebida com sucesso",
            "image_url": result["image_url"],
            "thumbnail_url": result["thumbnail_url"],
            "placeholder_blur": result["placeholder_blur"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_images_routes.route("/admin/remote-delete", methods=["DELETE"])
def remote_delete_image_api():
    token = request.headers.get("Authorization", "")
    expected_token = os.getenv("VPS_UPLOAD_TOKEN")

    if not token or token != f"Bearer {expected_token}":
        return jsonify({"error": "Token de autenticação inválido"}), 403

    data = request.get_json()
    image_url = data.get("image_url")
    if not image_url:
        return jsonify({"error": "URL da imagem não fornecida"}), 400

    try:
        delete_remote_image(image_url=image_url)
        return jsonify({"message": "Imagem deletada com sucesso"}), 200

    except Exception as e:
        return jsonify({"error": f"Erro ao apagar a imagem: {str(e)}"}), 500
    
    
@admin_images_routes.route("/admin/products/<int:product_id>/update-images", methods=["POST"])
@jwt_required()
@admin_required
def update_product_images(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Produto não encontrado"}), 404

    images_order = request.form.getlist('images_order[]')
    files = request.files.getlist('images')

    # Parse IDs que devem ser mantidos (1 query) 
    keep_ids = set()
    for item in images_order:
        if item.startswith('id:'):
            keep_ids.add(int(item.split(':')[1]))

    # Busca todas as imagens atuais do produto em uma única query
    all_current = ProductImage.query.filter_by(product_id=product_id).all()
    existing_images = {img.id: img for img in all_current}

    # Deleta fisicamente as que não estão na lista e remove do banco as que estão (para reinserir na nova ordem)
    for img in all_current:
        if img.id not in keep_ids:
            try:
                delete_remote_image(img.image_url)
            except Exception as e:
                current_app.logger.error(f"Falha ao deletar imagem remota: {str(e)}")
        db.session.delete(img)

    db.session.flush()

    new_image_ids = []

    for idx, item in enumerate(images_order):
        is_cover = (idx == 0)

        if item.startswith('file:'):
            file_idx = int(item.split(':')[1])
            file = files[file_idx]
            result = save_image(file, is_cover=is_cover, product_id=product_id)
            
            image_url = result["image_url"]
            thumbnail_url = result["thumbnail_url"]
            placeholder_blur = result["placeholder_blur"]
            
            image_public_url = image_url if flask_env == "production" else CDN_BASE_URL + "/" + image_url
            thumbnail_public_url = thumbnail_url if flask_env == "production" else CDN_BASE_URL + "/" + thumbnail_url
            
            img_row = ProductImage(
                product_id=product_id,
                image_url=image_url,
                image_public_url=image_public_url,
                is_cover=is_cover,
                thumbnail_url=thumbnail_url,
                thumbnail_public_url=thumbnail_public_url,
                placeholder_blur=placeholder_blur
            )
            db.session.add(img_row)
            db.session.flush()  # necessário para obter o ID gerado
            new_image_ids.append({"id": img_row.id, "image_url": image_url, "image_public_url": image_public_url, "is_cover": is_cover})

        elif item.startswith('id:'):
            img_id = int(item.split(':')[1])
            old_img = existing_images.get(img_id)
            if old_img:
                img_row = ProductImage(
                    product_id=product_id,
                    image_url=old_img.image_url,
                    image_public_url=old_img.image_public_url,
                    is_cover=is_cover,
                    thumbnail_url=old_img.thumbnail_url,
                    thumbnail_public_url=old_img.thumbnail_public_url,
                    placeholder_blur=old_img.placeholder_blur
                )
                db.session.add(img_row)
                # sem flush aqui — ID não é necessário na resposta para imagens existentes

    db.session.commit()
    return jsonify({"message": "Imagens atualizadas na nova ordem", "added": new_image_ids}), 200
############################################################################################


###################################### Upload de Imagens ######################################
@admin_images_routes.route("/admin/products/<int:product_id>/upload-images", methods=["POST"])
@jwt_required()
@admin_required
def upload_product_images(product_id):
    claims = get_jwt()
    if not claims.get("is_admin"):
        return jsonify({"error": "Acesso não autorizado"}), 403

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Produto não encontrado"}), 404

    if 'images' not in request.files:
        return jsonify({"error": "Nenhuma imagem enviada"}), 400

    files = request.files.getlist('images')
    saved_images = []

    for index, file in enumerate(files):
        try:
            # Primeira imagem é sempre capa
            is_cover = (index == 0)
            
            result = save_image(file, is_cover=is_cover, product_id=product.id)
            
            image_url = result["image_url"]
            thumbnail_url = result["thumbnail_url"]
            placeholder_blur = result["placeholder_blur"]
            
            if flask_env == "production":
                image_public_url = image_url
                thumbnail_public_url = thumbnail_url
            else:
                image_public_url = CDN_BASE_URL + "/" + image_url
                thumbnail_public_url = CDN_BASE_URL + "/" + thumbnail_url

            image = ProductImage(
                product_id=product.id,
                image_url=image_url,
                image_public_url=image_public_url,
                is_cover=is_cover,
                thumbnail_url=thumbnail_url,
                thumbnail_public_url=thumbnail_public_url,
                placeholder_blur=placeholder_blur
            )
            db.session.add(image)
            saved_images.append(image_url)

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    db.session.commit()
    return jsonify({"message": "Imagens enviadas com sucesso", "images": saved_images})
###################################################################################################


################################ Delete de Imagem ##########################################
@admin_images_routes.route("/admin/products/delete_image/<int:image_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_product_image(image_id):
    # 1. Buscar a imagem pelo ID
    image = ProductImage.query.get(image_id)
    if not image:
        return jsonify({"error": "Imagem não encontrada"}), 404

    # 2. Apagar imagem do disco local ou remotamente (VPS)
    try:
        delete_remote_image(image.image_url)
    except Exception as e:
        return jsonify({"error": f"Erro ao apagar a imagem: {str(e)}"}), 500

    # 3. Remover registro do banco
    try:
        db.session.delete(image)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erro ao remover imagem do banco: {str(e)}"}), 500

    return jsonify({"message": "Imagem deletada com sucesso", "image_id": image_id})
###############################################################################################



################################## Deletar TODAS as imagens de um produto ##################################
@admin_images_routes.route("/admin/products/<int:product_id>/delete-all-images", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_all_product_images(product_id):
    try:
        # 1. Buscar o produto e verificar existência
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"error": "Produto não encontrado"}), 404

        # 2. Buscar todas as imagens associadas ao produto
        images = ProductImage.query.filter_by(product_id=product_id).all()
        
        if not images:
            return jsonify({"message": "Nenhuma imagem encontrada para este produto"}), 200

        # 3. Deletar arquivos físicos e registros do banco
        deleted_count = 0
        errors = []
        
        for image in images:
            try:
                # 3.1. Deletar arquivo físico (local ou remoto)
                delete_remote_image(image.image_url)
                
                # 3.2. Remover registro do banco
                db.session.delete(image)
                deleted_count += 1
                
            except Exception as e:
                errors.append({
                    "image_id": image.id,
                    "error": str(e)
                })
        
        # 4. Commit das alterações no banco
        db.session.commit()
        
        # 5. Montar resposta
        response = {
            "message": f"{deleted_count}/{len(images)} imagens deletadas com sucesso",
            "product_id": product_id
        }
        
        if errors:
            response["errors"] = errors
            return jsonify(response), 207  # Status 207 = Multi-Status
            
        return jsonify(response), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erro geral: {str(e)}"}), 500
###########################################################################################################