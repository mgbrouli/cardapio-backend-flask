from flask import Flask, render_template, request, redirect, url_for
from model import db
import controller as ct
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'banco.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/', methods = ['GET'])
def index():
    
    produtos_com_imagens = ct.get_all_prod_with_images()
    return render_template('index.html', produto=produtos_com_imagens)

@app.route('/home', methods = ['GET'])
def home():
    
    produtos_com_imagens = ct.get_all_prod_with_images()
    return render_template('home.html', produto=produtos_com_imagens)

@app.route('/add', methods=['POST'])
def add_pizza():
    if request.method == "POST":
        nome_novo = request.form.get('nome')
        ingredientes_novo = request.form.get('ingredientes')
        preco_novo = request.form.get('preco')
        
        # Processar a imagem
        imagem_arquivo = request.files.get('image')
        nome_imagem = None
        imagem_dados = None
        
        if imagem_arquivo:
            nome_imagem = imagem_arquivo.filename
            imagem_dados = imagem_arquivo.read()
        
        try:
            preco_formatado = float(preco_novo)
            ct.create_prod(nome=nome_novo, ingredientes=ingredientes_novo, preco=preco_formatado, 
                          image_name=nome_imagem, image_data=imagem_dados)
        except (ValueError, TypeError):
            return "Preço invalido", 400
        return redirect(url_for('home'))

@app.route('/remove/<int:id>', methods=['DELETE'])
def delete(id):
    if ct.delete_prod(id=id):
        return '', 204
    else:
        return "Erro não funcao"

@app.route('/edit/<int:id>', methods=['POST'])
def edit_pizza(id):
    if request.method == "POST":
        nome_novo = request.form.get('nome')
        ingredientes_novo = request.form.get('ingredientes')
        preco_novo = request.form.get('preco')
        
        # Processar a imagem (opcional para edição)
        imagem_arquivo = request.files.get('imagem')
        nome_imagem = None
        imagem_dados = None
        
        if imagem_arquivo:
            nome_imagem = imagem_arquivo.filename
            imagem_dados = imagem_arquivo.read()
        
        try:
            preco_formatado = float(preco_novo)
            ct.update_prod(id=id, nome=nome_novo, ingredientes=ingredientes_novo, preco=preco_formatado,
                          image_name=nome_imagem, image_data=imagem_dados)
        except (ValueError, TypeError):
            return "Preço invalido", 400
        return redirect(url_for('home'))
    
@app.route("/config/<int:client_id>", methods=["GET", "POST"])
def config(client_id):
    if request.method == 'GET':
        return render_template('config.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80 ,debug=True)