# backend/rocca_app/routes/models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random
import string
from . import db


def generate_order_id():
    """Gera um ID único de 6 caracteres: 4 dígitos + 2 letras maiúsculas (ex: '4821RK').
    Garante unicidade consultando o banco antes de retornar."""
    while True:
        digits = ''.join(random.choices(string.digits, k=4))
        letters = ''.join(random.choices(string.ascii_uppercase, k=2))
        new_id = digits + letters
        if not Order.query.get(new_id):
            return new_id

# Inicialização do banco de dados

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    phone = db.Column(db.String(20), nullable=True)
    #is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamento com os pedidos (1:N)
    orders = db.relationship('Order', backref='user', lazy=True)
    carts = db.relationship('Cart', backref='user', lazy=True)


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    collection = db.Column(db.String(100))
    price = db.Column(db.Numeric(10, 2), nullable=False)
    fast_price = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    is_public = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Novos campos de envio
    weight = db.Column(db.Numeric(10, 2), nullable=False, default=0.00) # em KG
    dimensionC = db.Column(db.Numeric(10, 2), nullable=False, default=0.00) # Comp, em CM
    dimensionL = db.Column(db.Numeric(10, 2), nullable=False, default=0.00) # Largura, em CM
    dimensionA = db.Column(db.Numeric(10, 2), nullable=False, default=0.00) # Altura, em CM

    scheduled_publish_at = db.Column(db.DateTime, nullable=True, default=None)
    is_scheduled = db.Column(db.Boolean, default=False, nullable=False)

    # Ordenação na loja (ProductsView)
    sort_order = db.Column(db.Integer, nullable=False, default=9999)

    # Relacionamento com os itens do pedido (1:N)
    order_items = db.relationship('OrderItem', back_populates='product')
    cart_items = db.relationship('CartItem', back_populates='product')
    variants = db.relationship('ProductVariant', backref='product', lazy=True, cascade="all, delete-orphan", passive_deletes=True)
    images = db.relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")


    product_categories = db.relationship('ProductCategory', back_populates='product', cascade="all, delete-orphan")
    categories = db.relationship('Category', secondary='product_categories', viewonly=True)

    product_collections = db.relationship('ProductCollection', back_populates='product', cascade="all, delete-orphan")
    collections = db.relationship('Collection', secondary='product_collections', viewonly=True)


    @property
    def stock(self):
        return sum(variant.stock for variant in self.variants)
    


class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    image_public_url = db.Column(db.String(255), nullable=False)
    is_cover = db.Column(db.Boolean, default=False)
    thumbnail_url = db.Column(db.String(255), nullable=True)
    thumbnail_public_url = db.Column(db.String(255), nullable=True)
    placeholder_blur = db.Column(db.Text, nullable=True)

    product = db.relationship("Product", back_populates="images")




class ProductVariant(db.Model):
    __tablename__ = 'product_variant'

    product_variant_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    size = db.Column(db.String(10), nullable=False)  # P, M, G, GG ou "Único"
    stock = db.Column(db.Integer, nullable=False, default=0)

    order_items = db.relationship('OrderItem', back_populates='product_variant')
    cart_items = db.relationship('CartItem', back_populates='product_variant')


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    # Relacionamento reverso com os produtos
    product_categories = db.relationship('ProductCategory', back_populates='category', cascade="all, delete-orphan")
    products = db.relationship('Product', secondary='product_categories', viewonly=True)


class ProductCategory(db.Model):
    __tablename__ = 'product_categories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), primary_key=True)
    product_name = db.Column(db.String(100))  # Nome do produto no momento da associação
    category_name = db.Column(db.String(50))  # Nome da categoria no momento da associação
    highlight_order = db.Column(db.Integer, nullable=False, default=9999)  # Ordem no grid de destaques

    product = db.relationship('Product', back_populates='product_categories')
    category = db.relationship('Category', back_populates='product_categories')


class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    total = db.Column(db.Numeric(10, 2))
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id'), nullable=True)
    discount_amount = db.Column(db.Numeric(10, 2), nullable=True, default=0.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relacionamento com os itens do pedido (1:N)
    cart_items = db.relationship('CartItem', backref='cart', lazy=True)


class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    product_variant_id = db.Column(db.Integer, db.ForeignKey('product_variant.product_variant_id'), nullable=True)
    quantity = db.Column(db.Integer)
    price = db.Column(db.Numeric(10, 2))

    # Relacionamentos
    product = db.relationship('Product', back_populates='cart_items')
    product_variant = db.relationship('ProductVariant', back_populates='cart_items')


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.String(6), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    total = db.Column(db.Numeric(10, 2))
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id'), nullable=True)
    discount_amount = db.Column(db.Numeric(10, 2), nullable=True, default=0.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Novos campos de status e pagamento
    status = db.Column(db.String(50), default='pending') # Status do pedido (preparando, enviado, entregue...)
    payment_status = db.Column(db.String(50), default='pending') # approved, pending, rejected...
    payment_id = db.Column(db.String(100), nullable=True) # ID do pagamento no gateway (se houver) - String p/ evitar overflow
    payment_method = db.Column(db.String(50), nullable=True) # pix, credit_card...
    installments = db.Column(db.Integer, default=1)
    
    is_paid = db.Column(db.Boolean, default=False) # Mantendo por retrocompatibilidade por enquanto, mas a lógica usará payment_status

    # Campos de envio (frete - Melhor Envio)
    shipping_price = db.Column(db.Numeric(10, 2), nullable=True, default=0.00)
    shipping_service_name = db.Column(db.String(100), nullable=True)  # ex: "SEDEX", "PAC"
    shipping_service_id = db.Column(db.Integer, nullable=True)         # ID do serviço na Melhor Envio
    shipping_delivery_time = db.Column(db.Integer, nullable=True)      # Prazo em dias úteis

    # Endereço de entrega
    shipping_cep = db.Column(db.String(10), nullable=True)
    shipping_address = db.Column(db.String(255), nullable=True)        # Rua/Logradouro
    shipping_number = db.Column(db.String(20), nullable=True)
    shipping_complement = db.Column(db.String(100), nullable=True)     # Apartamento, bloco, etc.
    shipping_neighborhood = db.Column(db.String(100), nullable=True)   # Bairro
    shipping_city = db.Column(db.String(100), nullable=True)
    shipping_state = db.Column(db.String(2), nullable=True)            # UF (2 letras)

    # CPF do cliente para Melhor Envio
    customer_cpf = db.Column(db.String(14), nullable=True)

    # Relacionamento com os itens do pedido (1:N)
    order_items = db.relationship('OrderItem', backref='order', lazy=True)


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(6), db.ForeignKey('orders.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    product_variant_id = db.Column(db.Integer, db.ForeignKey('product_variant.product_variant_id'), nullable=True)
    quantity = db.Column(db.Integer)
    price = db.Column(db.Numeric(10, 2))

    # Relacionamentos
    product = db.relationship('Product', back_populates='order_items')
    product_variant = db.relationship('ProductVariant', back_populates='order_items')


class PricingItem(db.Model):
    __tablename__ = 'pricing_items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    cost = db.Column(db.Numeric(10, 2), default=0)
    price = db.Column(db.Numeric(10, 2), default=0)
    subsidy_frete = db.Column(db.Numeric(10, 2), default=0)
    ads = db.Column(db.Numeric(10, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class FastSale(db.Model):
    __tablename__ = 'fast_sales'

    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=True)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    pay_method = db.Column(db.String(50), nullable=False) # pix, dinheiro, cartao
    date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', backref='fast_sales')
    items = db.relationship('FastSaleItem', backref='fast_sale', cascade="all, delete-orphan")


class FastSaleItem(db.Model):
    __tablename__ = 'fast_sale_items'

    id = db.Column(db.Integer, primary_key=True)
    fast_sale_id = db.Column(db.Integer, db.ForeignKey('fast_sales.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product_variant_id = db.Column(db.Integer, db.ForeignKey('product_variant.product_variant_id'), nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    product = db.relationship('Product')
    product_variant = db.relationship('ProductVariant')


class Collection(db.Model):
    __tablename__ = 'collections'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    product_collections = db.relationship('ProductCollection', back_populates='collection', cascade="all, delete-orphan")
    products = db.relationship('Product', secondary='product_collections', viewonly=True)


class ProductCollection(db.Model):
    __tablename__ = 'product_collections'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    collection_id = db.Column(db.Integer, db.ForeignKey('collections.id', ondelete='CASCADE'), nullable=False)
    product_name = db.Column(db.String(100))
    collection_name = db.Column(db.String(100))

    product = db.relationship('Product', back_populates='product_collections')
    collection = db.relationship('Collection', back_populates='product_collections')


class Coupon(db.Model):
    __tablename__ = 'coupons'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    porcentagem = db.Column(db.Boolean, nullable=False, default=True)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    frete_gratis = db.Column(db.Boolean, nullable=False, default=False)
    is_active = db.Column(db.Boolean, nullable=False, default=False)
    data_inicio = db.Column(db.DateTime, nullable=True)
    data_fim = db.Column(db.DateTime, nullable=True)
    gasto_minimo = db.Column(db.Numeric(10, 2), nullable=True)
    gasto_maximo = db.Column(db.Numeric(10, 2), nullable=True)
    uso_individual = db.Column(db.Boolean, nullable=False, default=True)
    excluir_item_com_desconto = db.Column(db.Boolean, nullable=False, default=True)
    
    produtos = db.Column(db.Boolean, nullable=False, default=False)
    excluir_produtos = db.Column(db.Boolean, nullable=False, default=False)
    categorias = db.Column(db.Boolean, nullable=False, default=False)
    excluir_categorias = db.Column(db.Boolean, nullable=False, default=False)
    colecoes = db.Column(db.Boolean, nullable=False, default=False)
    excluir_colecoes = db.Column(db.Boolean, nullable=False, default=False)
    
    limite_uso = db.Column(db.Integer, nullable=True)
    limite_por_conta = db.Column(db.Integer, nullable=True)
    vezes_usado = db.Column(db.Integer, nullable=False, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    product_coupons = db.relationship('ProductCoupon', back_populates='coupon', cascade="all, delete-orphan")
    category_coupons = db.relationship('CategoryCoupon', back_populates='coupon', cascade="all, delete-orphan")
    collection_coupons = db.relationship('CollectionCoupon', back_populates='coupon', cascade="all, delete-orphan")


class ProductCoupon(db.Model):
    __tablename__ = 'product_coupons'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    excluir = db.Column(db.Boolean, nullable=False, default=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id', ondelete='CASCADE'), nullable=False)
    product_name = db.Column(db.String(100))
    coupon_name = db.Column(db.String(100))

    product = db.relationship('Product')
    coupon = db.relationship('Coupon', back_populates='product_coupons')


class CategoryCoupon(db.Model):
    __tablename__ = 'category_coupons'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    excluir = db.Column(db.Boolean, nullable=False, default=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='CASCADE'), nullable=False)
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id', ondelete='CASCADE'), nullable=False)
    category_name = db.Column(db.String(50))
    coupon_name = db.Column(db.String(100))

    category = db.relationship('Category')
    coupon = db.relationship('Coupon', back_populates='category_coupons')


class CollectionCoupon(db.Model):
    __tablename__ = 'collection_coupons'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    excluir = db.Column(db.Boolean, nullable=False, default=False)
    collection_id = db.Column(db.Integer, db.ForeignKey('collections.id', ondelete='CASCADE'), nullable=False)
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id', ondelete='CASCADE'), nullable=False)
    collection_name = db.Column(db.String(100))
    coupon_name = db.Column(db.String(100))

    collection = db.relationship('Collection')
    coupon = db.relationship('Coupon', back_populates='collection_coupons')


class AppSetting(db.Model):
    """
    Tabela de configurações da aplicação.
    Usada para persistir tokens OAuth2 (Melhor Envio) entre restarts do servidor.
    
    Chaves usadas:
        - me_access_token: Token de acesso da Melhor Envio
        - me_refresh_token: Token de refresh da Melhor Envio
    """
    __tablename__ = 'app_settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get_value(key, default=None):
        """Busca um valor pela chave. Retorna default se não existir."""
        setting = AppSetting.query.filter_by(key=key).first()
        return setting.value if setting else default

    @staticmethod
    def set_value(key, value):
        """Cria ou atualiza um valor pela chave."""
        setting = AppSetting.query.filter_by(key=key).first()
        if setting:
            setting.value = value
            setting.updated_at = datetime.utcnow()
        else:
            setting = AppSetting(key=key, value=value)
            db.session.add(setting)
        db.session.commit()


class EmailVerificationToken(db.Model):
    """
    Tabela para armazenar tokens OTP de verificação de e-mail.
    Utilizada em cadastro de conta e troca de e-mail.
    """
    __tablename__ = 'email_verification_tokens'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, index=True)
    code = db.Column(db.String(6), nullable=False)
    purpose = db.Column(db.String(20), nullable=False)  # 'register' ou 'change_email'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Só em troca de e-mail
    # Dados temporarios do futuro usuário (para registro)
    temp_name = db.Column(db.String(100), nullable=True)
    temp_password_hash = db.Column(db.String(255), nullable=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def generate_code():
        """Gera um código OTP numérico de 6 dígitos."""
        return ''.join(random.choices(string.digits, k=6))

    @staticmethod
    def create_token(email, purpose, user_id=None, temp_name=None, temp_password_hash=None):
        """Remove tokens anteriores para o mesmo email+purpose e cria um novo."""
        # Remove tokens anteriores
        EmailVerificationToken.query.filter_by(email=email, purpose=purpose).delete()
        code = EmailVerificationToken.generate_code()
        token = EmailVerificationToken(
            email=email,
            code=code,
            purpose=purpose,
            user_id=user_id,
            temp_name=temp_name,
            temp_password_hash=temp_password_hash,
            expires_at=datetime.utcnow() + timedelta(minutes=15)
        )
        db.session.add(token)
        db.session.commit()
        return token
