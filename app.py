from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from model import Empresa, Usuario, db
import controller as ct
import os

app = Flask(__name__)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Redireciona para cá se não estiver logado


app.config['SECRET_KEY'] = 'uma-chave-muito-segura-e-secreta-123'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'banco.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def landing():
    # Se o usuário estiver logado, podemos sugerir que ele vá para o painel
    return render_template('landing.html')

@app.route('/<int:empresa_id>', methods = ['GET'])
def index(empresa_id):
    
    empresa = Empresa.query.get_or_404(empresa_id)

    if not empresa.ativo:
        return "Este cardápio está temporariamente suspenso. Entre em contato com o administrador.", 403

    produtos_com_imagens = ct.get_all_prod_with_images(empresa_id)
    return render_template('index.html', produto=produtos_com_imagens, empresa=empresa)

@login_manager.user_loader
def loader_user(user_id):
    return Usuario.query.get(int(user_id))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        nome_loja = request.form.get('nome_loja')
        whats = request.form.get('whatsapp')

        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            # Aqui você pode usar Flash Messages ou apenas retornar um erro
            return "Este e-mail já está cadastrado. Tente fazer login.", 400
        try:
        # 1. Cria a Empresa primeiro
            nova_empresa = Empresa(name_est=nome_loja, whatsapp=whats)
            db.session.add(nova_empresa)
            db.session.flush() # Gera o ID da empresa sem fechar a transação

            # 2. Cria o Usuário vinculado a essa empresa
            hash_senha = generate_password_hash(senha)
            novo_usuario = Usuario(email=email, senha=hash_senha, empresa_id=nova_empresa.id)
            
            db.session.add(novo_usuario)
            db.session.commit()
        
            return redirect(url_for('landing'))
        except Exception as e:
            db.session.rollback()
            return f"Erro ao cadastrar: {str(e)}", 500

    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        user = Usuario.query.filter_by(email=email).first()

        if user and check_password_hash(user.senha, senha):
            login_user(user)
            return redirect(url_for('home')) # Vai para a home da empresa dele
    return render_template('login.html')

@app.route('/home')
@login_required
def home():
    
    empresa_id = current_user.empresa_id
    produtos_com_imagens = ct.get_all_prod_with_images(empresa_id)
    return render_template('home.html', produto=produtos_com_imagens, empresa_id=empresa_id)

@app.route('/add<int:empresa_id>', methods=['POST'])
def add_pizza(empresa_id):
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
            ct.create_prod(empresa_id=empresa_id,nome=nome_novo, ingredientes=ingredientes_novo, preco=preco_formatado, 
                          image_name=nome_imagem, image_data=imagem_dados)
        except (ValueError, TypeError):
            return "Preço invalido", 400
        return redirect(url_for('home', empresa_id=empresa_id))

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
    
@app.route("/config/<int:empresa_id>", methods=["GET", "POST"])
def config(empresa_id):
    empresa = Empresa.query.get_or_404(empresa_id)

    if request.method == 'POST':
        # Dados Gerais
        empresa.name_est = request.form.get('nome_est')
        empresa.whatsapp = request.form.get('whatsapp')
        empresa.short_description = request.form.get('descricao')
        
        # Endereço
        empresa.logradouro = request.form.get('logradouro')
        empresa.cidade = request.form.get('cidade')
        # ... (demais campos)

        # Aparência
        empresa.primary_color = request.form.get('primary_color')

        db.session.commit()
        return redirect(url_for('home', empresa_id=empresa.id))

    return render_template('config.html', empresa=empresa)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80 ,debug=True)