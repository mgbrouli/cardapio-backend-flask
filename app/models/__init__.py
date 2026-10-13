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
