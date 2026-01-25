# App package
from app.models import db

__all__ = ['db', 'create_app']


def create_app(config=None):
    """Factory function para criar a aplicação Flask"""
    from flask import Flask, redirect, url_for, request
    from flask_login import LoginManager, login_required, current_user
    from app.models import Usuario
    from app.routes.public_routes import public_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.empresa_routes import empresa_bp
    from app.routes.produto_routes import produto_bp
    from config import get_config

    import os
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, 'templates'),
        static_folder=os.path.join(base_dir, 'static'),
    )
    
    # Carregando configurações
    if config is None:
        config = get_config()
    
    app.config.from_object(config)
    
    # Inicializando extensões
    db.init_app(app)
    
    # Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor faça login para acessar esta página'
    
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))
    
    # Criando tabelas do banco de dados
    with app.app_context():
        db.create_all()
    
    # Registrando blueprints
    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(empresa_bp, url_prefix='/empresa')
    app.register_blueprint(produto_bp)
    
    # Rotas legadas para compatibilidade
    @app.route('/add/<int:empresa_id>', methods=['POST'])
    @login_required
    def add_pizza(empresa_id):
        """Rota legada - processa o formulário diretamente"""
        from app.services.produto_service import ProdutoService
        
        if current_user.empresa_id != empresa_id:
            return "Acesso negado", 403
        
        nome = request.form.get('nome')
        ingredientes = request.form.get('ingredientes')
        preco = request.form.get('preco')
        
        # Processar imagem
        imagem_arquivo = request.files.get('image')
        nome_imagem = None
        imagem_dados = None
        
        if imagem_arquivo:
            nome_imagem = imagem_arquivo.filename
            imagem_dados = imagem_arquivo.read()
        
        service = ProdutoService()
        resultado = service.criar_produto(
            empresa_id=empresa_id,
            nome=nome,
            ingredientes=ingredientes,
            preco=preco,
            image_name=nome_imagem,
            image_data=imagem_dados
        )
        
        if resultado['success']:
            return redirect(url_for('empresa.home'))
        else:
            return resultado['message'], 400
    
    @app.route('/remove/<int:id>', methods=['DELETE'])
    def delete(id):
        """Rota legada - redireciona para nova rota"""
        from app.services.produto_service import ProdutoService
        service = ProdutoService()
        resultado = service.deletar_produto(id)
        
        if resultado['success']:
            return '', 204
        else:
            return resultado['message'], 400
    
    @app.route('/edit/<int:id>', methods=['POST'])
    @login_required
    def edit_pizza(id):
        """Edita pizza - processa POST diretamente para preservar dados e arquivos"""
        from app.services.produto_service import ProdutoService
        from app.models import Produtos
        
        if not current_user.is_authenticated:
            return "Acesso negado", 403
        
        # Verificar se o produto pertence à empresa do usuário
        produto = Produtos.query.get(id)
        if not produto or produto.empresa_id != current_user.empresa_id:
            return "Acesso negado", 403
        
        nome = request.form.get('nome')
        ingredientes = request.form.get('ingredientes')
        preco = request.form.get('preco')
        
        # Processar imagem (opcional)
        imagem_arquivo = request.files.get('imagem')
        nome_imagem = None
        imagem_dados = None
        
        if imagem_arquivo:
            nome_imagem = imagem_arquivo.filename
            imagem_dados = imagem_arquivo.read()
        
        service = ProdutoService()
        resultado = service.atualizar_produto(
            produto_id=id,
            nome=nome,
            ingredientes=ingredientes,
            preco=preco,
            image_name=nome_imagem,
            image_data=imagem_dados
        )
        
        if resultado['success']:
            return redirect(url_for('empresa.home'))
        else:
            return resultado['message'], 400
    
    @app.route("/config/<int:empresa_id>", methods=["GET", "POST"])
    @login_required
    def config(empresa_id):
        """Rota legada - redireciona para nova rota"""
        if current_user.empresa_id != empresa_id:
            return "Acesso negado", 403
        return redirect(url_for('empresa.config', empresa_id=empresa_id))
    
    return app
