from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Produtos(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    nome = db.Column(db.String(100), nullable=False)
    ingredientes = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)