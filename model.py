from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Produtos(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    nome = db.Column(db.String(100), nullable=False)
    ingredientes = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    imagens = db.relationship('Imagens', backref='produto', lazy=True)

class Imagens(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.LargeBinary, nullable=False)

    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    

class Empresa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Dados Gerais
    name_est = db.Column(db.String(100), nullable=False)
    cnpj_est = db.Column(db.String(20), nullable=True) # CNPJ pode ser opcional
    short_description = db.Column(db.String(255), nullable=True)
    whatsapp = db.Column(db.String(20), nullable=False) # Corrigido para String
    
    # Endereço
    logradouro = db.Column(db.String(150), nullable=True)
    bairro = db.Column(db.String(100), nullable=True)
    cidade = db.Column(db.String(100), nullable=True)
    estado = db.Column(db.String(2), nullable=True)
    cep = db.Column(db.String(10), nullable=True)
    
    # Aparência (Cores e Caminhos das Imagens)
    primary_color = db.Column(db.String(7), default="#0d6efd") # Armazena Hexadecimal ex: #FFFFFF
    bg_color = db.Column(db.String(7), default="#ffffff")
    text_color = db.Column(db.String(7), default="#212529")
    
    logo_path = db.Column(db.String(255), nullable=True)   # Caminho do arquivo no servidor
    banner_path = db.Column(db.String(255), nullable=True) # Caminho do arquivo no servidor

    produtos = db.relationship('Produtos', backref='empresa', lazy=True)
    imagens = db.relationship('Imagens', backref='empresa', lazy=True)

    def __repr__(self):
        return f'<Empresa {self.name_est}>'
    
class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False) # Guardaremos a senha criptografada
    
    # Cada usuário é dono de uma empresa
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'))
    empresa = db.relationship('Empresa', backref=db.backref('dono', uselist=False))