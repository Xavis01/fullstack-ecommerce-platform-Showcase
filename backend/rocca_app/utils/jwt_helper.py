from flask_jwt_extended import create_access_token
from datetime import timedelta

def generate_token(user_id, email, name, is_admin=False):
    """
    Gera um token JWT com o user_id como identidade (sub)
    e inclui email e is_admin como claims adicionais.
    """
    additional_claims = {
        "email": email,
        "is_admin": is_admin,
        "name": name
    }
    return create_access_token(
        identity=str(user_id),
        additional_claims=additional_claims,
        expires_delta=timedelta(minutes=60))