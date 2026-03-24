# backend/rocca_app/routes/user_routes.py

from flask import Blueprint, request, jsonify, current_app
import re
import os
from ..utils.password_utils import hash_password, verify_password, needs_rehash
from ..models import User, db, EmailVerificationToken
from ..utils.jwt_helper import generate_token
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from flask_mail import Mail, Message
from datetime import timedelta
from .. import limiter


def _mask_cpf(cpf: str) -> str:
    """Mascara CPF para exibição: ***.xxx.xxx-**"""
    if not cpf:
        return None
    digits = re.sub(r'\D', '', cpf)
    if len(digits) == 11:
        return f"***.{digits[3:6]}.{digits[6:9]}-**"
    return cpf


user_routes = Blueprint('user_routes', __name__)


# ─── URL da logo para e-mails ────────────────────────────────────────────────
def _get_logo_url() -> str:
    frontend_url = os.environ.get('FRONTEND_URL', '').rstrip('/')
    if frontend_url:
        return f"{frontend_url}/ROCCABehe.png"
    return ''  # sem URL configurada: a imagem simplesmente não aparece



# ─────────────────────────────────────────────────────────────────────────────
# Helper: enviar e-mail de verificação
# ─────────────────────────────────────────────────────────────────────────────
def send_verification_email(to_email: str, code: str, purpose: str):
    from .. import mail

    if purpose == 'register':
        subject = "Rocca Internazionale — Confirme seu e-mail"
        action_text = "confirmar seu cadastro"
    else:
        subject = "Rocca Internazionale — Confirme seu novo e-mail"
        action_text = "confirmar a alteração do seu e-mail"

    html_body = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin:0;padding:0;background:#f5f3e8;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f3e8;padding:40px 0;">
        <tr>
          <td align="center">
            <table width="480" cellpadding="0" cellspacing="0"
                   style="background:#fffdf2;border:1.5px solid #0f2301;border-radius:4px;overflow:hidden;max-width:90vw;">
              <!-- Header -->
              <tr>
                <td style="background:#0f2301;padding:24px 40px;text-align:center;">
                  <img src="{_get_logo_url()}" alt="Rocca Internazionale"
                       style="height:40px;width:auto;display:block;margin:0 auto;" />
                </td>
              </tr>
              <!-- Body -->
              <tr>
                <td style="padding:40px 40px 32px;">
                  <p style="margin:0 0 16px;font-size:15px;font-weight:300;color:#3a5528;line-height:1.6;">
                    Para {action_text}, use o código abaixo. Ele é válido por <strong>15 minutos</strong>.
                  </p>
                  <!-- OTP Code -->
                  <div style="margin:32px 0;text-align:center;">
                    <span style="display:inline-block;background:#0f2301;color:#fffdf2;
                                 font-size:36px;font-weight:300;letter-spacing:0.25em;
                                 padding:18px 36px;border-radius:6px;font-family:monospace;">
                      {code}
                    </span>
                  </div>
                  <p style="margin:0;font-size:13px;font-weight:300;color:#8c9e78;line-height:1.6;">
                    Se você não solicitou isso, pode ignorar este e-mail com segurança.
                  </p>
                </td>
              </tr>
              <!-- Footer -->
              <tr>
                <td style="padding:20px 40px;border-top:1px solid #eaddcf;text-align:center;">
                  <p style="margin:0;font-size:12px;font-weight:300;color:#aab89a;font-style:italic;">
                    Rocca Internazionale &copy; 2026 — Todos os direitos reservados
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """

    msg = Message(
        subject=subject,
        recipients=[to_email],
        html=html_body
    )
    mail.send(msg)


# ─────────────────────────────────────────────────────────────────────────────
# Helper: enviar e-mail de redefinição de senha
# ─────────────────────────────────────────────────────────────────────────────
def send_reset_password_email(to_email: str, code: str):
    from .. import mail

    html_body = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin:0;padding:0;background:#f5f3e8;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f3e8;padding:40px 0;">
        <tr>
          <td align="center">
            <table width="480" cellpadding="0" cellspacing="0"
                   style="background:#fffdf2;border:1.5px solid #0f2301;border-radius:4px;overflow:hidden;max-width:90vw;">
              <tr>
                <td style="background:#0f2301;padding:24px 40px;text-align:center;">
                  <img src="{_get_logo_url()}" alt="Rocca Internazionale"
                       style="height:40px;width:auto;display:block;margin:0 auto;" />
                </td>
              </tr>
              <tr>
                <td style="padding:40px 40px 32px;">
                  <p style="margin:0 0 8px;font-size:18px;font-weight:300;font-style:italic;color:#0f2301;">
                    Redefinição de Senha
                  </p>
                  <p style="margin:0 0 16px;font-size:15px;font-weight:300;color:#3a5528;line-height:1.6;">
                    Recebemos uma solicitação para redefinir a senha da sua conta.<br>
                    Use o código abaixo. Ele é válido por <strong>15 minutos</strong>.
                  </p>
                  <div style="margin:32px 0;text-align:center;">
                    <span style="display:inline-block;background:#0f2301;color:#fffdf2;
                                 font-size:36px;font-weight:300;letter-spacing:0.25em;
                                 padding:18px 36px;border-radius:6px;font-family:monospace;">
                      {code}
                    </span>
                  </div>
                  <p style="margin:0;font-size:13px;font-weight:300;color:#8c9e78;line-height:1.6;">
                    Se você não solicitou a redefinição de senha, ignore este e-mail.<br>
                    Sua senha permanecerá a mesma.
                  </p>
                </td>
              </tr>
              <tr>
                <td style="padding:20px 40px;border-top:1px solid #eaddcf;text-align:center;">
                  <p style="margin:0;font-size:12px;font-weight:300;color:#aab89a;font-style:italic;">
                    Rocca Internazionale &copy; 2026 — Todos os direitos reservados
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """

    msg = Message(
        subject="Rocca Internazionale — Redefinição de Senha",
        recipients=[to_email],
        html=html_body
    )
    mail.send(msg)



# ─────────────────────────────────────────────────────────────────────────────
# Helper: enviar e-mail de confirmação de pedido
# ─────────────────────────────────────────────────────────────────────────────
def send_order_confirmation_email(order, user):
    """Envia e-mail de confirmação de compra após pagamento aprovado."""
    from .. import mail

    is_pickup = order.shipping_service_name == 'Retirada'

    # ── Monta linhas da tabela de itens ───────────────────────────────────────
    items_rows = ''
    for item in order.order_items:
        product  = item.product
        variant  = item.product_variant
        name     = product.name if product else 'Produto'
        size     = variant.size if variant else ''
        size_str = f' — {size}' if size and size.lower() not in ('unico', 'único') else ''
        subtotal = float(item.price * item.quantity)
        items_rows += (
            f'<tr>'
            f'<td style="padding:10px 0;border-bottom:1px solid #eaddcf;font-size:14px;font-weight:300;color:#3a5528;">{name}{size_str}</td>'
            f'<td style="padding:10px 0;border-bottom:1px solid #eaddcf;font-size:14px;font-weight:300;color:#3a5528;text-align:center;">{item.quantity}</td>'
            f'<td style="padding:10px 0;border-bottom:1px solid #eaddcf;font-size:14px;font-weight:300;color:#3a5528;text-align:right;">R$ {subtotal:.2f}</td>'
            f'</tr>'
        )

    # ── Totais ────────────────────────────────────────────────────────────────
    discount_str = ''
    if order.discount_amount and float(order.discount_amount) > 0:
        discount_str = (
            f'<tr>'
            f'<td colspan="2" style="padding:6px 0;font-size:13px;font-weight:300;color:#8c9e78;text-align:right;">Desconto (cupom)</td>'
            f'<td style="padding:6px 0;font-size:13px;font-weight:300;color:#9a382d;text-align:right;">- R$ {float(order.discount_amount):.2f}</td>'
            f'</tr>'
        )

    shipping_str = ''
    if not is_pickup:
        shipping_price = float(order.shipping_price) if order.shipping_price else 0.0
        shipping_label = order.shipping_service_name or 'Frete'
        shipping_str = (
            f'<tr>'
            f'<td colspan="2" style="padding:6px 0;font-size:13px;font-weight:300;color:#8c9e78;text-align:right;">{shipping_label}</td>'
            f'<td style="padding:6px 0;font-size:13px;font-weight:300;color:#3a5528;text-align:right;">R$ {shipping_price:.2f}</td>'
            f'</tr>'
        )

    # ── Bloco de encerramento: retirada vs envio ──────────────────────────────
    wpp_msg = f'Salve fam! Gostaria de agendar a retirada do meu pedido #{order.id}.'
    wpp_url = f'https://wa.me/5527996657004?text={wpp_msg}'

    if is_pickup:
        closing_block = (
            '<div style="margin:32px 0;background:#f0efe9;border:1px solid #eaddcf;border-radius:6px;padding:20px 24px;">'
            '<p style="margin:0 0 4px;font-size:13px;font-weight:300;color:#8c9e78;text-transform:uppercase;letter-spacing:0.08em;">M&eacute;todo de entrega</p>'
            '<p style="margin:0 0 12px;font-size:15px;font-weight:300;color:#0f2301;">&#128205; Retirada no QG da Rocca</p>'
            '<p style="margin:0 0 4px;font-size:13px;font-weight:300;color:#3a5528;line-height:1.6;">'
            'Av. Eng. Charles Bitran, 435 &mdash; Jardim Camburi, Vit&oacute;ria - ES, 29092-270</p>'
            '<p style="margin:8px 0 0;font-size:12px;font-weight:300;color:#8c9e78;font-style:italic;">'
            '&#9200; Responderemos em at&eacute; 24 horas para combinar o hor&aacute;rio.</p>'
            '</div>'
            '<div style="text-align:center;margin:0 0 24px;">'
            f'<a href="{wpp_url}" style="display:inline-block;background:#25D366;color:#ffffff;'
            'font-size:15px;font-weight:400;letter-spacing:0.04em;padding:14px 32px;border-radius:6px;text-decoration:none;">'
            '&#128242; Agendar Retirada pelo WhatsApp</a>'
            '</div>'
        )
    else:
        closing_block = (
            '<div style="margin:32px 0;background:#f0efe9;border:1px solid #eaddcf;border-radius:6px;padding:20px 24px;">'
            '<p style="margin:0 0 8px;font-size:15px;font-weight:300;color:#0f2301;">&#128666; Seu pedido est&aacute; sendo preparado para envio!</p>'
            '</div>'
        )

    first_name = user.name.split()[0] if user.name else 'cliente'

    html_body = (
        '<!DOCTYPE html><html lang="pt-BR"><head>'
        '<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">'
        '</head><body style="margin:0;padding:0;background:#f5f3e8;font-family:\'Helvetica Neue\',Helvetica,Arial,sans-serif;">'
        '<table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f3e8;padding:40px 0;"><tr><td align="center">'
        '<table width="520" cellpadding="0" cellspacing="0" style="background:#fffdf2;border:1.5px solid #0f2301;border-radius:4px;overflow:hidden;max-width:90vw;">'

        # Header
        f'<tr><td style="background:#0f2301;padding:24px 40px;text-align:center;">'
        f'<img src="{_get_logo_url()}" alt="Rocca Internazionale" style="height:40px;width:auto;display:block;margin:0 auto;" />'
        f'</td></tr>'

        # Body
        '<tr><td style="padding:40px 40px 32px;">'
        f'<p style="margin:0 0 4px;font-size:20px;font-weight:300;font-style:italic;color:#0f2301;">Pedido confirmado! &#10003;</p>'
        f'<p style="margin:0 0 24px;font-size:14px;font-weight:300;color:#8c9e78;">Ol&aacute;, {first_name}! Seu pagamento foi aprovado.</p>'

        # Order badge
        f'<div style="display:inline-block;background:#0f2301;color:#fffdf2;font-size:13px;font-weight:300;'
        f'letter-spacing:0.15em;padding:6px 16px;border-radius:3px;margin-bottom:28px;">'
        f'PEDIDO #{order.id}</div>'

        # Items table
        '<table width="100%" cellpadding="0" cellspacing="0">'
        '<thead><tr>'
        '<th style="padding:8px 0;border-bottom:2px solid #0f2301;font-size:11px;font-weight:400;color:#8c9e78;text-transform:uppercase;letter-spacing:0.08em;text-align:left;">Produto</th>'
        '<th style="padding:8px 0;border-bottom:2px solid #0f2301;font-size:11px;font-weight:400;color:#8c9e78;text-transform:uppercase;letter-spacing:0.08em;text-align:center;">Qtd</th>'
        '<th style="padding:8px 0;border-bottom:2px solid #0f2301;font-size:11px;font-weight:400;color:#8c9e78;text-transform:uppercase;letter-spacing:0.08em;text-align:right;">Subtotal</th>'
        '</tr></thead>'
        f'<tbody>{items_rows}</tbody>'
        '<tfoot>'
        f'{discount_str}'
        f'{shipping_str}'
        f'<tr>'
        f'<td colspan="2" style="padding:12px 0 0;font-size:15px;font-weight:400;color:#0f2301;text-align:right;border-top:2px solid #0f2301;">Total</td>'
        f'<td style="padding:12px 0 0;font-size:15px;font-weight:400;color:#0f2301;text-align:right;border-top:2px solid #0f2301;">R$ {float(order.total):.2f}</td>'
        f'</tr></tfoot></table>'

        f'{closing_block}'

        '<p style="margin:0;font-size:13px;font-weight:300;color:#8c9e78;line-height:1.6;">'
        'Qualquer d&uacute;vida, entre em contato pelo nosso WhatsApp ou Instagram.<br>Obrigado por comprar na Rocca! &#128420;</p>'
        '</td></tr>'

        # Footer
        '<tr><td style="padding:20px 40px;border-top:1px solid #eaddcf;text-align:center;">'
        '<p style="margin:0;font-size:12px;font-weight:300;color:#aab89a;font-style:italic;">'
        'Rocca Internazionale &copy; 2026 &mdash; Todos os direitos reservados</p>'
        '</td></tr>'

        '</table></td></tr></table></body></html>'
    )

    msg = Message(
        subject=f"Rocca Internazionale \u2014 Pedido #{order.id} confirmado! \u2705",
        recipients=[user.email],
        html=html_body
    )
    try:
        mail.send(msg)
    except Exception as e:
        current_app.logger.error(f"[EMAIL PEDIDO] Erro ao enviar confirmacao do pedido {order.id}: {e}")



@user_routes.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    claims = get_jwt()

    return jsonify({
        'id': user_id,
        'name': claims.get("name"),
        'email': claims.get("email"),
        'is_admin': claims.get("is_admin"),
        'phone': user.phone if user else None
    }), 200
##############################################################


################### Listagem de Pedidos do Usuário ##########################
@user_routes.route('/user/orders', methods=['GET'])
@jwt_required()
@limiter.limit("30 per minute")
def get_my_orders():
    from sqlalchemy.orm import joinedload
    from ..models import Order, OrderItem, Coupon
    user_id = get_jwt_identity()

    from ..models import User
    orders = Order.query.filter_by(user_id=user_id).options(
        joinedload(Order.order_items).joinedload(OrderItem.product),
        joinedload(Order.order_items).joinedload(OrderItem.product_variant)
    ).order_by(Order.created_at.desc()).all()
    user = User.query.get(user_id)
    
    orders_list = []

    for order in orders:
        order_data = {
            'order_id': order.id,
            'date': (order.created_at - timedelta(hours=3)).strftime('%d/%m/%Y %H:%M') if order.created_at else 'N/A',
            'total': float(order.total) if order.total is not None else 0.0,
            'is_paid': order.is_paid,
            'payment_status': order.payment_status,
            'payment_method': order.payment_method,
            'payment_id': order.payment_id,
            'installments': order.installments or 1,
            'discount_amount': float(order.discount_amount) if order.discount_amount else 0.0,
            'coupon_code': None,
            'coupon_percentage': False,
            'coupon_value': 0.0,
            'customer_cpf': _mask_cpf(order.customer_cpf),
            'customer_phone': user.phone if user else None,
            'shipping': {
                'price': float(order.shipping_price) if order.shipping_price else 0.0,
                'service_name': order.shipping_service_name,
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
            
        orders_list.append(order_data)

    return jsonify(orders_list), 200
#########################################################################


################## Atualizar Cadastro do Usuário ##########################
@user_routes.route('/user/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'Usuário não encontrado.'}), 404

    data = request.get_json()
    new_name = data.get('name')
    new_email = data.get('email')
    new_password = data.get('password')
    new_phone = data.get('phone')

    # Validação e Atualização de nome
    if new_name:
        if not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s\'-]+$", new_name):
            return jsonify({'error': 'O nome não pode conter caracteres especiais ou números'}), 400
        user.name = new_name

    # Se o e-mail mudou, disparar verificação em vez de atualizar direto
    if new_email and new_email != user.email:
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+$", new_email):
            return jsonify({'error': 'Formato de e-mail inválido'}), 400
        existing = User.query.filter_by(email=new_email).first()
        if existing:
            return jsonify({'error': 'Este e-mail já está em uso por outra conta.'}), 409

        # Salva nome/telefone/senha antes de pedir verificação
        if new_phone is not None:
            user.phone = new_phone.strip() if new_phone else None
        if new_password:
            if len(new_password) < 6:
                return jsonify({'error': 'A nova senha deve ter pelo menos 6 caracteres.'}), 400
            user.password_hash = hash_password(new_password)
        db.session.commit()

        # Gera OTP e envia para o NOVO e-mail
        token = EmailVerificationToken.create_token(
            email=new_email,
            purpose='change_email',
            user_id=user_id
        )
        try:
            send_verification_email(new_email, token.code, 'change_email')
        except Exception as e:
            current_app.logger.error(f"Erro ao enviar e-mail de verificação: {e}")
            # Mesmo com erro de envio, retornar 200 para não bloquear
            return jsonify({
                'email_verification_required': True,
                'pending_email': new_email,
                'warning': 'Não foi possível enviar o e-mail. Verifique as configurações SMTP.'
            }), 200

        return jsonify({
            'email_verification_required': True,
            'pending_email': new_email,
            'message': f'Enviamos um código de verificação para {new_email}. Insira o código para confirmar a alteração.'
        }), 200

    # Se o e-mail não mudou, atualizar os demais campos normalmente
    if new_password:
        if len(new_password) < 6:
            return jsonify({'error': 'A nova senha deve ter pelo menos 6 caracteres.'}), 400
        user.password_hash = hash_password(new_password)

    if new_phone is not None:
        user.phone = new_phone.strip() if new_phone else None
        
    db.session.commit()
    
    # Gerar um novo token JWT pois o nome ou email (claims) podem ter mudado
    new_token = generate_token(user.id, user.email, user.name, user.is_admin)

    return jsonify({
        'message': 'Perfil atualizado com sucesso.',
        'token': new_token,
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'is_admin': user.is_admin,
            'phone': user.phone
        }
    }), 200
###########################################################################


############### Cadastro de usuário (valida dados, envia OTP) ##############
@user_routes.route('/register', methods=['POST'])
@limiter.limit("5 per minute; 20 per hour")
def register():
    data = request.get_json()

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({'error': 'Preencha todos os campos'}), 400

    if not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s\'-]+$", name):
        return jsonify({'error': 'O nome não pode conter caracteres especiais ou números'}), 400

    if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+$", email):
        return jsonify({'error': 'Formato de e-mail inválido'}), 400

    if len(password) < 6:
        return jsonify({'error': 'A senha deve ter pelo menos 6 caracteres'}), 400

    # Verifica se o e-mail já existe
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'E-mail já cadastrado'}), 409

    # Hash bcrypt da senha e cria token de verificação (ainda não salva o usuário)
    hashed_password = hash_password(password)
    token = EmailVerificationToken.create_token(
        email=email,
        purpose='register',
        temp_name=name,
        temp_password_hash=hashed_password
    )

    try:
        send_verification_email(email, token.code, 'register')
    except Exception as e:
        current_app.logger.error(f"Erro ao enviar e-mail de verificação: {e}")
        return jsonify({
            'error': 'Não foi possível enviar o e-mail de verificação. Verifique as configurações SMTP.',
            'details': str(e)
        }), 500

    return jsonify({
        'message': f'Código de verificação enviado para {email}. Confirme para concluir o cadastro.',
        'email': email
    }), 200
#########################################################################


############### Esqueceu a Senha — Envia OTP ##############################
@user_routes.route('/auth/forgot-password', methods=['POST'])
@limiter.limit("5 per hour")
def forgot_password():
    data = request.get_json()
    email = data.get('email', '').strip().lower()

    if not email:
        return jsonify({'error': 'Informe o e-mail.'}), 400

    # Busca o usuário mas NÃO revela se o e-mail existe (evita enumeração)
    user = User.query.filter_by(email=email).first()
    if not user:
        # Retorna 200 genérico para não revelar que o e-mail não existe
        return jsonify({'message': 'Se este e-mail estiver cadastrado, você receberá um código em instantes.'}), 200

    token = EmailVerificationToken.create_token(
        email=email,
        purpose='reset_password',
        user_id=user.id
    )

    try:
        send_reset_password_email(email, token.code)
    except Exception as e:
        current_app.logger.error(f"Erro ao enviar e-mail de reset: {e}")
        return jsonify({
            'error': 'Não foi possível enviar o e-mail. Verifique as configurações SMTP.',
            'details': str(e)
        }), 500

    return jsonify({
        'message': 'Se este e-mail estiver cadastrado, você receberá um código em instantes.',
        'email': email
    }), 200
###########################################################################


############### Esqueceu a Senha — Reseta com OTP ########################
@user_routes.route('/auth/reset-password', methods=['POST'])
@limiter.limit("10 per hour")
def reset_password():
    from datetime import datetime
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    code = data.get('code', '').strip()
    new_password = data.get('new_password', '')

    if not email or not code or not new_password:
        return jsonify({'error': 'email, code e new_password são obrigatórios.'}), 400

    if len(new_password) < 6:
        return jsonify({'error': 'A nova senha deve ter pelo menos 6 caracteres.'}), 400

    token = EmailVerificationToken.query.filter_by(
        email=email, purpose='reset_password'
    ).first()

    if not token:
        return jsonify({'error': 'Código não encontrado. Solicite um novo código.'}), 404

    if datetime.utcnow() > token.expires_at:
        db.session.delete(token)
        db.session.commit()
        return jsonify({'error': 'Código expirado. Solicite um novo código.'}), 410

    if token.code != code:
        return jsonify({'error': 'Código incorreto. Tente novamente.'}), 400

    user = User.query.get(token.user_id)
    if not user:
        db.session.delete(token)
        db.session.commit()
        return jsonify({'error': 'Usuário não encontrado.'}), 404

    user.password_hash = hash_password(new_password)
    db.session.delete(token)
    db.session.commit()

    return jsonify({'message': 'Senha redefinida com sucesso! Faça login com sua nova senha.'}), 200
###########################################################################



############## Enviar / Reenviar código de verificação ##################
@user_routes.route('/auth/send-verification', methods=['POST'])
@limiter.limit("5 per minute; 15 per hour")
def send_verification():
    data = request.get_json()
    email = data.get('email')
    purpose = data.get('purpose')  # 'register' ou 'change_email'

    if not email or not purpose:
        return jsonify({'error': 'email e purpose são obrigatórios'}), 400

    if purpose not in ('register', 'change_email'):
        return jsonify({'error': 'purpose inválido'}), 400

    # Para reenvio de cadastro, busca dados temporários do token anterior
    existing_token = EmailVerificationToken.query.filter_by(
        email=email, purpose=purpose
    ).first()

    if purpose == 'register':
        if not existing_token:
            return jsonify({'error': 'Sessão de cadastro expirada. Tente se cadastrar novamente.'}), 400
        # Cria novo token mantendo os dados temporários
        token = EmailVerificationToken.create_token(
            email=email,
            purpose='register',
            temp_name=existing_token.temp_name,
            temp_password_hash=existing_token.temp_password_hash
        )
    else:  # change_email
        # Precisa estar autenticado
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
        except Exception:
            return jsonify({'error': 'Autenticação necessária para trocar e-mail'}), 401

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'Este e-mail já está em uso.'}), 409

        token = EmailVerificationToken.create_token(
            email=email,
            purpose='change_email',
            user_id=user_id
        )

    try:
        send_verification_email(email, token.code, purpose)
    except Exception as e:
        current_app.logger.error(f"Erro ao reenviar e-mail: {e}")
        return jsonify({'error': 'Falha ao enviar e-mail. Tente novamente.', 'details': str(e)}), 500

    return jsonify({'message': f'Código reenviado para {email}.'}), 200
#########################################################################


############## Verificar código OTP e concluir ação ####################
@user_routes.route('/auth/verify-email', methods=['POST'])
@limiter.limit("15 per hour")
def verify_email():
    from datetime import datetime
    data = request.get_json()
    email = data.get('email')
    code = data.get('code')
    purpose = data.get('purpose')  # 'register' ou 'change_email'

    if not email or not code or not purpose:
        return jsonify({'error': 'email, code e purpose são obrigatórios'}), 400

    token = EmailVerificationToken.query.filter_by(
        email=email, purpose=purpose
    ).first()

    if not token:
        return jsonify({'error': 'Código não encontrado. Solicite um novo código.'}), 404

    if datetime.utcnow() > token.expires_at:
        db.session.delete(token)
        db.session.commit()
        return jsonify({'error': 'Código expirado. Solicite um novo código.'}), 410

    if token.code != code.strip():
        return jsonify({'error': 'Código incorreto. Tente novamente.'}), 400

    # ── Cadastro: criar o usuário e logar ──────────────────────────────────
    if purpose == 'register':
        # Verifica novamente se o e-mail já foi cadastrado (corrida de condição)
        existing = User.query.filter_by(email=email).first()
        if existing:
            db.session.delete(token)
            db.session.commit()
            return jsonify({'error': 'E-mail já cadastrado.'}), 409

        new_user = User(
            name=token.temp_name,
            email=email,
            password_hash=token.temp_password_hash
        )
        db.session.add(new_user)
        db.session.delete(token)
        db.session.commit()

        # Gerar token JWT e logar automaticamente
        jwt_token = generate_token(new_user.id, new_user.email, new_user.name, new_user.is_admin)

        return jsonify({
            'message': 'Cadastro realizado com sucesso! Bem-vindo(a) à Rocca.',
            'token': jwt_token,
            'user': {
                'id': new_user.id,
                'name': new_user.name,
                'email': new_user.email,
                'is_admin': new_user.is_admin,
                'phone': None
            }
        }), 201

    # ── Troca de e-mail: atualizar o usuário ──────────────────────────────
    if purpose == 'change_email':
        user = User.query.get(token.user_id)
        if not user:
            db.session.delete(token)
            db.session.commit()
            return jsonify({'error': 'Usuário não encontrado.'}), 404

        # Verifica se o novo e-mail já foi tomado por outro usuário enquanto aguardava
        existing = User.query.filter_by(email=email).first()
        if existing and existing.id != user.id:
            db.session.delete(token)
            db.session.commit()
            return jsonify({'error': 'Este e-mail já está em uso.'}), 409

        user.email = email
        db.session.delete(token)
        db.session.commit()

        new_jwt = generate_token(user.id, user.email, user.name, user.is_admin)

        return jsonify({
            'message': 'E-mail atualizado com sucesso!',
            'token': new_jwt,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'is_admin': user.is_admin,
                'phone': user.phone
            }
        }), 200

    return jsonify({'error': 'purpose inválido'}), 400
#########################################################################


#################### Login de usuário ######################################
@user_routes.route('/login', methods=['POST'])
@limiter.limit("10 per minute; 50 per hour")
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email e senha são obrigatórios.'}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not verify_password(password, user.password_hash):
        return jsonify({'error': 'Credenciais inválidas.'}), 401

    # Migração transparente: se o hash ainda é werkzeug, re-hasheia com bcrypt
    if user and needs_rehash(user.password_hash):
        user.password_hash = hash_password(password)
        db.session.commit()

    # Gera o token JWT com as claims
    token = generate_token(user.id, user.email, user.name, user.is_admin)

    return jsonify({
        'message': 'Login realizado com sucesso.',
        'token': token,
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'is_admin': user.is_admin
        }
    }), 200
###########################################################################

################## Recuperar Código PIX do Pedido #########################
@user_routes.route('/user/orders/<string:order_id>/pix', methods=['GET'])
@jwt_required()
@limiter.limit("15 per minute")
def get_pix_data(order_id):
    from ..models import Order
    import mercadopago
    import os
    
    user_id = get_jwt_identity()
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    
    if not order:
        return jsonify({'error': 'Pedido não encontrado.'}), 404

    if order.payment_method != 'pix' or not order.payment_id:
        return jsonify({'error': 'Não há código PIX disponível para este pedido.'}), 400

    mp_access_token = os.environ.get("MP_ACCESS_TOKEN")
    if not mp_access_token:
        # Fallback de dev
        return jsonify({'error': 'Gateway de pagamento não configurado.'}), 500

    try:
        sdk = mercadopago.SDK(mp_access_token)
        payment_info = sdk.payment().get(order.payment_id)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erro SDK: {str(e)}'}), 500

    payment_data = payment_info.get("response", {})
    if payment_info.get("status") != 200 or not payment_data:
        return jsonify({'error': 'Falha ao recuperar dados do Mercado Pago.', 'details': payment_info}), 502

    # Verifica se a transação do PIX tem a propriedade ticket_url e qr_code
    transaction_data = payment_data.get('point_of_interaction', {}).get('transaction_data', {})
    
    return jsonify({
        'qr_code': transaction_data.get('qr_code'),
        'qr_code_base64': transaction_data.get('qr_code_base64'),
        'ticket_url': transaction_data.get('ticket_url'),
        'status': payment_data.get('status')
    }), 200
#########################################################################

################## Verificar Status do Pedido #########################
@user_routes.route('/user/orders/<string:order_id>/status', methods=['GET'])
@jwt_required()
@limiter.limit("20 per minute")
def get_order_status(order_id):
    from ..models import Order, ProductVariant, User
    import mercadopago
    import os
    
    user_id = get_jwt_identity()
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    user = User.query.get(user_id)
    
    if not order:
        return jsonify({'error': 'Pedido não encontrado.'}), 404

    # Se ainda estiver pendente localmente, tenta verificar no Mercado Pago
    if not order.is_paid and order.payment_id:
        mp_access_token = os.environ.get("MP_ACCESS_TOKEN")
        if mp_access_token:
            try:
                sdk = mercadopago.SDK(mp_access_token)
                payment_info = sdk.payment().get(order.payment_id)
                if payment_info["status"] == 200:
                    payment = payment_info["response"]
                    status = payment.get("status")
                    
                    if status == "approved" and not order.is_paid:
                        order.status = "paid"
                        order.payment_status = "approved"
                        order.is_paid = True
                        
                        # Baixa estoque
                        for order_item in order.order_items:
                            variant = ProductVariant.query.get(order_item.product_variant_id)
                            if variant:
                                variant.stock -= order_item.quantity
                        
                        # Incrementa uso do cupom se existir
                        if order.coupon_id:
                            from .public_coupon_routes import Coupon
                            coupon = Coupon.query.get(order.coupon_id)
                            if coupon:
                                coupon.vezes_usado += 1
                        
                        db.session.commit()
                        # Enviar e-mail de confirmação após aprovação via polling PIX
                        try:
                            send_order_confirmation_email(order, user)
                        except Exception as email_err:
                            print(f"[EMAIL] Erro ao enviar confirmação (polling): {email_err}")
                    elif status != order.payment_status:
                        order.payment_status = status
                        db.session.commit()
            except Exception as e:
                print(f"Erro ao verificar status no MP: {e}")

    return jsonify({
        'order_id': order.id,
        'status': order.status,
        'payment_status': order.payment_status,
        'is_paid': order.is_paid
    }), 200
#########################################################################


################## Cancelar Pedido e Restaurar Carrinho #########################
@user_routes.route('/user/orders/<string:order_id>/cancel', methods=['DELETE'])
@jwt_required()
def cancel_order(order_id):
    from ..models import Order, Cart, CartItem
    
    user_id = get_jwt_identity()
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    
    if not order:
        return jsonify({'error': 'Pedido não encontrado.'}), 404

    if order.status != 'pending' or order.payment_status != 'pending':
        return jsonify({'error': 'Apenas pedidos aguardando pagamento podem ser cancelados.'}), 400

    # Busca ou cria o carrinho aberto do usuário
    cart = Cart.query.filter_by(user_id=user_id, is_active=True).first()
    if not cart:
        cart = Cart(user_id=user_id, is_active=True, total=0.0)
        db.session.add(cart)
        db.session.flush()

    for order_item in list(order.order_items):
        # Verifica se o item já existe no carrinho para somar a quantidade
        cart_item = CartItem.query.filter_by(
            cart_id=cart.id,
            product_id=order_item.product_id,
            product_variant_id=order_item.product_variant_id
        ).first()

        if cart_item:
            cart_item.quantity += order_item.quantity
        else:
            new_cart_item = CartItem(
                cart_id=cart.id,
                product_id=order_item.product_id,
                product_variant_id=order_item.product_variant_id,
                quantity=order_item.quantity,
                price=order_item.price
            )
            db.session.add(new_cart_item)
        
        db.session.delete(order_item)

    # Recalcula e salva o total do carrinho
    db.session.flush()
    cart.total = sum(item.price * item.quantity for item in cart.cart_items)

    db.session.delete(order)
    db.session.commit()

    return jsonify({'message': 'Pedido cancelado. Os itens foram devolvidos ao seu carrinho.'}), 200
#########################################################################
