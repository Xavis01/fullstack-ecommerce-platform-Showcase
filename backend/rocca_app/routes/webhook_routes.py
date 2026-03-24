import os
import hmac
import hashlib
import mercadopago
from flask import Blueprint, request, jsonify
from ..models import db, Order, ProductVariant

webhook_routes = Blueprint('webhook_routes', __name__)


def _verify_mp_signature() -> bool:
    """
    Valida a assinatura HMAC-SHA256 enviada pelo Mercado Pago no header x-signature.
    Retorna True se válida (ou se MP_WEBHOOK_SECRET não estiver configurado no env).
    Documentação: https://www.mercadopago.com.br/developers/pt/docs/your-integrations/notifications/webhooks
    """
    mp_secret = os.environ.get("MP_WEBHOOK_SECRET")
    if not mp_secret:
        # Sem secret definido: modo dev/sem validação (não bloqueia em dev)
        return True

    x_signature = request.headers.get("x-signature", "")
    x_request_id = request.headers.get("x-request-id", "")
    data_id = request.args.get("data.id", "") or (request.get_json(silent=True) or {}).get("data", {}).get("id", "")

    if not x_signature:
        return False

    # Extrai ts e v1 do header
    parts = {}
    for part in x_signature.split(","):
        if "=" in part:
            k, v = part.strip().split("=", 1)
            parts[k] = v

    ts = parts.get("ts", "")
    received_hash = parts.get("v1", "")

    if not ts or not received_hash:
        return False

    # Monta o manifesto conforme documentação do MP
    manifest = f"id:{data_id};request-id:{x_request_id};ts:{ts};"
    expected = hmac.new(
        mp_secret.encode("utf-8"),
        manifest.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, received_hash)


@webhook_routes.route('/webhooks/mercadopago', methods=['POST'])
def mercadopago_webhook():
    # ── Verificação de assinatura ──────────────────────────────────────────────
    if not _verify_mp_signature():
        return jsonify({"error": "Invalid signature"}), 401

    data = request.args.to_dict()
    if not data:
        data = request.get_json() or {}

    action = data.get("action")
    payment_id = data.get("data.id") or (data.get("data", {}).get("id"))

    # Verifica se é uma notificação de pagamento (payment.created ou payment.updated)
    if (action and action.startswith("payment.")) or (data.get("type") == "payment"):
        if not payment_id:
            return jsonify({"status": "ignored", "reason": "No payment id provided"}), 200

        mp_access_token = os.environ.get("MP_ACCESS_TOKEN")
        if not mp_access_token:
            return jsonify({"error": "MP_ACCESS_TOKEN not configured"}), 500

        sdk = mercadopago.SDK(mp_access_token)
        payment_info = sdk.payment().get(payment_id)
        
        if payment_info["status"] == 200:
            payment = payment_info["response"]
            external_reference = payment.get("external_reference")
            status = payment.get("status")

            if external_reference:
                order = Order.query.get(external_reference)
                if order:
                    # Só atualiza e baixa estoque se o status mudou para aprovado e não estava pago antes
                    if status == "approved" and not order.is_paid:
                        order.status = "paid"
                        order.payment_status = "approved"
                        order.is_paid = True
                        
                        # Diminui estoque
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

                    else:
                        order.payment_status = status
                        
                    db.session.commit()

                    # Enviar e-mail de confirmação se aprovado
                    if status == 'approved':
                        try:
                            from .user_routes import send_order_confirmation_email
                            from ..models import User
                            user = User.query.get(order.user_id)
                            if user:
                                send_order_confirmation_email(order, user)
                        except Exception as email_err:
                            print(f"[EMAIL] Erro ao enviar confirmação via webhook: {email_err}")
    
    return jsonify({"status": "received"}), 200
