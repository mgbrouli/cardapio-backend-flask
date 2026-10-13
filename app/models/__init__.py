from sqlalchemy import DateTime

from app.database import db


class Produtos(db.Model):
    __tablename__ = "produtos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    ingredientes = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)

    empresa_id = db.Column(db.Integer, db.ForeignKey("empresa.id"), nullable=False)
    imagens = db.relationship(
        "Imagens", backref="produto", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Produto {self.nome}>"


class Imagens(db.Model):
    __tablename__ = "imagens"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.LargeBinary, nullable=False)

    produto_id = db.Column(db.Integer, db.ForeignKey("produtos.id"), nullable=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresa.id"), nullable=False)

    def __repr__(self):
        return f"<Imagem {self.name}>"


class Empresa(db.Model):
    __tablename__ = "empresa"

    id = db.Column(db.Integer, primary_key=True)
    name_est = db.Column(db.String(100), nullable=False)
    cnpj_est = db.Column(db.String(20), nullable=True)
    short_description = db.Column(db.String(255), nullable=True)
    whatsapp = db.Column(db.String(20), nullable=False)

    logradouro = db.Column(db.String(150), nullable=True)
    bairro = db.Column(db.String(100), nullable=True)
    cidade = db.Column(db.String(100), nullable=True)
    estado = db.Column(db.String(2), nullable=True)
    cep = db.Column(db.String(10), nullable=True)

    primary_color = db.Column(db.String(7), default="#0d6efd")
    bg_color = db.Column(db.String(7), default="#ffffff")
    text_color = db.Column(db.String(7), default="#212529")

    logo_path = db.Column(db.String(255), nullable=True)
    banner_path = db.Column(db.String(255), nullable=True)

    produtos = db.relationship(
        "Produtos", backref="empresa", lazy=True, cascade="all, delete-orphan"
    )
    imagens = db.relationship(
        "Imagens", backref="empresa", lazy=True, cascade="all, delete-orphan"
    )

    plano = db.Column(db.String(20), default="gratis")
    ativo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<Empresa {self.name_est}>"


class Usuario(db.Model):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)

    empresa_id = db.Column(db.Integer, db.ForeignKey("empresa.id"))
    empresa = db.relationship("Empresa", backref=db.backref("dono", uselist=False))

    def __repr__(self):
        return f"<Usuario {self.email}>"


class UserActivity(db.Model):
    __tablename__ = "user_activity"

    user_id = db.Column(
        db.Integer, db.ForeignKey("usuario.id", ondelete="CASCADE"), primary_key=True
    )
    last_seen_at = db.Column(DateTime(timezone=True), nullable=False)


class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_token"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash = db.Column(db.String(64), unique=True, nullable=False)
    expires_at = db.Column(DateTime(timezone=True), nullable=False)
    created_at = db.Column(DateTime(timezone=True), nullable=False)


class EmailVerification(db.Model):
    __tablename__ = "email_verification"

    user_id = db.Column(
        db.Integer, db.ForeignKey("usuario.id", ondelete="CASCADE"), primary_key=True
    )
    token_hash = db.Column(db.String(64), unique=True, nullable=True)
    expires_at = db.Column(DateTime(timezone=True), nullable=True)
    requested_at = db.Column(DateTime(timezone=True), nullable=False)
    verified_at = db.Column(DateTime(timezone=True), nullable=True)


class AuthRateLimit(db.Model):
    __tablename__ = "auth_rate_limit"

    key_hash = db.Column(db.String(64), primary_key=True)
    window_started_at = db.Column(DateTime(timezone=True), nullable=False, index=True)
    attempt_count = db.Column(db.Integer, nullable=False, default=0)
    blocked_until = db.Column(DateTime(timezone=True), nullable=True)


class Subscription(db.Model):
    __tablename__ = "subscription"

    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(20), nullable=False, default="asaas")
    empresa_id = db.Column(
        db.Integer, db.ForeignKey("empresa.id", ondelete="CASCADE"), nullable=False
    )
    plano = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    payment_link_id = db.Column(db.String(100), unique=True, nullable=False)
    payment_url = db.Column(db.String(500), nullable=False)
    provider_subscription_id = db.Column(db.String(100), nullable=True, index=True)
    updated_at = db.Column(DateTime(timezone=True), nullable=False)


class WebhookEvent(db.Model):
    __tablename__ = "webhook_event"

    event_id = db.Column(db.String(100), primary_key=True)
    received_at = db.Column(DateTime(timezone=True), nullable=False)


class PlatformSetting(db.Model):
    __tablename__ = "platform_setting"

    key = db.Column(db.String(100), primary_key=True)
    value = db.Column(db.String(255), nullable=False)
