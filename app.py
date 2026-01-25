"""Aplicação principal Flask"""
from flask import Flask
from flask_login import LoginManager
from app.models import db, Usuario
from app.routes.public_routes import public_bp
from app.routes.auth_routes import auth_bp
from app.routes.empresa_routes import empresa_bp
from app.routes.produto_routes import produto_bp
from config import get_config


def create_app(config=None):
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    
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
    
    return app


# Criar aplicação
app = create_app()

# Rotas antigas (mantidas para compatibilidade)
@app.route('/add/<int:empresa_id>', methods=['POST'])
@app.route('/add/<int:empresa_id>', methods=['POST'])
def add_pizza(empresa_id):
    # Rota legada mantida para compatibilidade, usar /produto/add/<int:empresa_id>
    from flask_login import current_user, login_required
    
    if not current_user.is_authenticated or current_user.empresa_id != empresa_id:
        return "Acesso negado", 403
    
    # Redireciona para nova rota
    return redirect(url_for('produto.add_produto', empresa_id=empresa_id))


@app.route('/remove/<int:id>', methods=['DELETE'])
@app.route('/remove/<int:id>', methods=['DELETE'])
def delete(id):
    # Rota legada mantida para compatibilidade, usar /produto/delete/<int:produto_id>
    from app.services.produto_service import ProdutoService
    
    service = ProdutoService()
    resultado = service.deletar_produto(id)
    
    if resultado['success']:
        return '', 204
    else:
        return resultado['message'], 400


@app.route('/edit/<int:id>', methods=['POST'])
@app.route('/edit/<int:id>', methods=['POST'])
def edit_pizza(id):
    # Rota legada mantida para compatibilidade, usar /produto/edit/<int:produto_id>
    from flask_login import current_user, login_required
    
    if not current_user.is_authenticated:
        return "Acesso negado", 403
    
    # Redireciona para nova rota
    return redirect(url_for('produto.edit_produto', produto_id=id))


@app.route("/config/<int:empresa_id>", methods=["GET", "POST"])
@login_required
def config(empresa_id):
    # Rota legada mantida para compatibilidade, usar /empresa/config/<int:empresa_id>
    return redirect(url_for('empresa.config', empresa_id=empresa_id))


if __name__ == '__main__':
    from flask_login import login_required
    app.run(host="0.0.0.0", port=80, debug=True)