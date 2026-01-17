from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Produtos(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    nome = db.Column(db.String(100), nullable=False)
    ingredientes = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    

class Imagens(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.LargeBinary, nullable=False)

    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)