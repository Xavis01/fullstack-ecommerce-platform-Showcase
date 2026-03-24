#backend\rocca_app\utils\upload_utils.py

import os
import io
import base64
import requests
from flask import current_app
from werkzeug.utils import secure_filename
from ..models import db, ProductImage 
import uuid  
from PIL import Image as PILImage, ImageOps


# ======================== Constantes de Otimização ========================
MAX_ORIGINAL_WIDTH = 2000      # Largura máxima da imagem original (px)
THUMBNAIL_WIDTH = 600          # Largura do thumbnail para grid da shop (px)
PLACEHOLDER_WIDTH = 20         # Largura do placeholder blur (px)
WEBP_QUALITY_ORIGINAL = 85     # Qualidade WebP da imagem original
WEBP_QUALITY_THUMBNAIL = 80    # Qualidade WebP do thumbnail
WEBP_QUALITY_PLACEHOLDER = 50  # Qualidade WebP do placeholder
THUMBS_SUBDIR = "thumbs"       # Subdiretório para thumbnails
# =========================================================================


def allowed_file(filename):
    ALLOWED_EXTENSIONS = current_app.config.get("ALLOWED_EXTENSIONS", {"png", "jpg", "jpeg", "webp"})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _process_image(file_bytes):
    """
    Processa uma imagem com Pillow:
    - Converte para RGB (remove alpha channel se existir)
    - Redimensiona o original para MAX_ORIGINAL_WIDTH
    - Gera thumbnail (THUMBNAIL_WIDTH)
    - Gera placeholder blur (PLACEHOLDER_WIDTH) como base64 data URI
    
    Retorna: (original_bytes, thumbnail_bytes, placeholder_base64)
    """
    img = PILImage.open(io.BytesIO(file_bytes))
    
    # Aplicar rotação EXIF (fotos de celular armazenam rotação nos metadados)
    img = ImageOps.exif_transpose(img)
    
    # Converter para RGB se necessário (RGBA, P, etc)
    if img.mode in ('RGBA', 'P', 'LA'):
        background = PILImage.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if 'A' in img.mode else None)
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Preservar aspect ratio
    original_width, original_height = img.size
    aspect_ratio = original_height / original_width
    
    # 1. Original otimizado (max 2000px de largura)
    if original_width > MAX_ORIGINAL_WIDTH:
        new_height = int(MAX_ORIGINAL_WIDTH * aspect_ratio)
        img_original = img.resize((MAX_ORIGINAL_WIDTH, new_height), PILImage.LANCZOS)
    else:
        img_original = img.copy()
    
    original_buffer = io.BytesIO()
    img_original.save(original_buffer, format='WEBP', quality=WEBP_QUALITY_ORIGINAL, method=4)
    original_bytes_out = original_buffer.getvalue()
    
    # 2. Thumbnail (600px de largura)
    thumb_height = int(THUMBNAIL_WIDTH * aspect_ratio)
    img_thumb = img.resize((THUMBNAIL_WIDTH, thumb_height), PILImage.LANCZOS)
    
    thumb_buffer = io.BytesIO()
    img_thumb.save(thumb_buffer, format='WEBP', quality=WEBP_QUALITY_THUMBNAIL, method=4)
    thumb_bytes_out = thumb_buffer.getvalue()
    
    # 3. Placeholder blur (20px de largura) como base64
    placeholder_height = int(PLACEHOLDER_WIDTH * aspect_ratio)
    img_placeholder = img.resize((PLACEHOLDER_WIDTH, placeholder_height), PILImage.LANCZOS)
    
    placeholder_buffer = io.BytesIO()
    img_placeholder.save(placeholder_buffer, format='WEBP', quality=WEBP_QUALITY_PLACEHOLDER, method=4)
    placeholder_base64 = "data:image/webp;base64," + base64.b64encode(placeholder_buffer.getvalue()).decode('utf-8')
    
    return original_bytes_out, thumb_bytes_out, placeholder_base64


def save_image(file, is_cover=False, product_id=None, env=None):
    """
    Salva uma imagem processada (WebP, thumbnail, placeholder).
    
    Retorna dict: {
        "image_url": str,           # URL da imagem original (WebP otimizada)
        "thumbnail_url": str,       # URL do thumbnail
        "placeholder_blur": str     # Base64 data URI do placeholder
    }
    """
    if not allowed_file(file.filename):
        raise ValueError("Arquivo não permitido")

    folder = current_app.config["UPLOAD_FOLDER"]
    upload_env = current_app.config["UPLOAD_ENV"]

    if upload_env == "dev":
        upload_mode = "remote"
    else:
        upload_mode = "local"

    # Define nome novo do arquivo (sempre .webp agora)
    if product_id is not None:
        unique_id = uuid.uuid4().hex[:8]
        if is_cover:
            filename = f"{product_id}_cover_{unique_id}.webp"
        else:
            filename = f"{product_id}_{unique_id}.webp"
    else:
        base_name = file.filename.rsplit('.', 1)[0]
        filename = secure_filename(f"{base_name}.webp")

    
    if upload_mode == "local":
        # Ler bytes do arquivo e processar com Pillow
        file_bytes = file.read()
        original_bytes, thumb_bytes, placeholder_base64 = _process_image(file_bytes)
        
        # VPS (upload local)
        if env == "dev":
            image_url = "/uploads/dev/" + filename
            thumb_url = "/uploads/dev/" + THUMBS_SUBDIR + "/" + filename
            folder = "dados_sensiveis"
        else:
            image_url = "/uploads/prod/" + filename
            thumb_url = "/uploads/prod/" + THUMBS_SUBDIR + "/" + filename
            folder = current_app.config["UPLOAD_FOLDER"]
        
        # Criar diretórios
        os.makedirs(folder, exist_ok=True)
        thumbs_folder = os.path.join(folder, THUMBS_SUBDIR)
        os.makedirs(thumbs_folder, exist_ok=True)
        
        # Salvar imagem original (WebP otimizada)
        original_path = os.path.join(folder, filename)
        with open(original_path, 'wb') as f:
            f.write(original_bytes)
        
        # Salvar thumbnail
        thumb_path = os.path.join(thumbs_folder, filename)
        with open(thumb_path, 'wb') as f:
            f.write(thumb_bytes)

        return {
            "image_url": image_url,
            "thumbnail_url": thumb_url,
            "placeholder_blur": placeholder_base64
        }
        

    elif upload_mode == "remote":
        # Máquina local (envia imagem para a VPS para processamento)
        vps_url = os.getenv("VPS_UPLOAD_URL")
        upload_token = os.getenv("VPS_UPLOAD_TOKEN")
        if not vps_url or not upload_token:
            raise RuntimeError("VPS_UPLOAD_URL ou VPS_UPLOAD_TOKEN não configurados")

        upload_endpoint = f"{vps_url}/api/admin/remote-upload"

        files = {'file': (filename, file.read(), file.mimetype)}
        data = {
            "is_cover": str(is_cover).lower(),
            "product_id": product_id
        }
        headers = {
            "Authorization": f"Bearer {upload_token}"
        }

        response = requests.post(upload_endpoint, files=files, data=data, headers=headers)

        if response.status_code != 200:
            raise RuntimeError(f"Erro ao enviar imagem remotamente: {response.text}")

        result = response.json()
        return {
            "image_url": result.get("image_url"),
            "thumbnail_url": result.get("thumbnail_url"),
            "placeholder_blur": result.get("placeholder_blur")
        }

    else:
        raise ValueError("UPLOAD_MODE inválido")
    

def delete_remote_image(image_url: str):
    """Deleta uma imagem e seu thumbnail correspondente."""
    upload_env = current_app.config["UPLOAD_ENV"]
    if upload_env == "dev":
        upload_mode = "remote"
    else:
        upload_mode = "local"
        

    if upload_mode == "local":
        base_path = "dados_sensiveis"
        
        # Deletar imagem original
        image_path = base_path + image_url
        if os.path.exists(image_path):
            os.remove(image_path)
        
        # Deletar thumbnail correspondente (mesmo nome, dentro de thumbs/)
        # Ex: /uploads/prod/file.webp -> /uploads/prod/thumbs/file.webp
        image_dir = os.path.dirname(image_url)
        image_filename = os.path.basename(image_url)
        thumb_url = os.path.join(image_dir, THUMBS_SUBDIR, image_filename)
        # Tentar com extensão .webp também (caso o original fosse .jpg mas o thumb é .webp)
        thumb_path = base_path + thumb_url
        if os.path.exists(thumb_path):
            os.remove(thumb_path)
        else:
            # Tentar com extensão .webp
            thumb_webp = os.path.splitext(thumb_path)[0] + ".webp"
            if os.path.exists(thumb_webp):
                os.remove(thumb_webp)

    elif upload_mode == "remote":
        # Executa o delete remotamente (VPS)
        vps_url = os.getenv("VPS_UPLOAD_URL")
        upload_token = os.getenv("VPS_UPLOAD_TOKEN")
        if not vps_url or not upload_token:
            raise RuntimeError("VPS_UPLOAD_URL ou VPS_UPLOAD_TOKEN não configurados")

        delete_endpoint = f"{vps_url}/api/admin/remote-delete"
        headers = {
            "Authorization": f"Bearer {upload_token}"
        }
        data = {
            "image_url": image_url
        }

        response = requests.delete(delete_endpoint, json=data, headers=headers)

        if response.status_code != 200:
            raise RuntimeError(f"Erro ao deletar imagem remotamente: {response.text}\n delete_endpoint = {delete_endpoint}")

    else:
        raise ValueError("UPLOAD_MODE inválido")
