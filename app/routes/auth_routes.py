"""Rotas de autenticação"""
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user
from app.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)

auth_service = AuthService()


@auth_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    """Registro de novo usuário"""
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        nome_loja = request.form.get('nome_loja')
        whatsapp = request.form.get('whatsapp')
        
        resultado = auth_service.registrar_usuario(email, senha, nome_loja, whatsapp)
        
        if resultado['success']:
            return redirect(url_for('auth.login'))
        else:
            return resultado['message'], 400
    
    return render_template('cadastro.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login do usuário"""
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        resultado = auth_service.validar_credenciais(email, senha)
        
        if resultado['success']:
            login_user(resultado['usuario'])
            return redirect(url_for('empresa.home'))
        else:
            return resultado['message'], 400
    
    return render_template('landing.html')


@auth_bp.route('/logout')
def logout():
    """Logout do usuário"""
    logout_user()
    return redirect(url_for('auth.login'))
