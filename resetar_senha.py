#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para resetar senha sem apagar dados"""

from app import create_app, db
from app.models import Usuario
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    print('🔧 RESETANDO SENHA DO USUÁRIO')
    print('='*60)
    
    # Encontrar usuário
    usuario = Usuario.query.filter_by(email='wtnbrouli@gmail.com').first()
    
    if not usuario:
        print('❌ Usuário não encontrado!')
        exit(1)
    
    print(f'✅ Usuário encontrado: {usuario.email}')
    print(f'   Empresa: {usuario.empresa_id}')
    print(f'   ID: {usuario.id}')
    
    # Resetar senha
    nova_senha = '123456'
    usuario.senha = generate_password_hash(nova_senha)
    db.session.commit()
    
    print(f'\n✅ Senha resetada!')
    print(f'   Nova senha: {nova_senha}')
    
    # Verificar que funcionou
    from app.services.auth_service import AuthService
    service = AuthService()
    resultado = service.validar_credenciais(usuario.email, nova_senha)
    
    if resultado['success']:
        print(f'\n✅ Teste de login: OK')
        print(f'\nℹ️  Dados preservados:')
        print(f'   Email: {usuario.email}')
        print(f'   Empresa ID: {usuario.empresa_id}')
    else:
        print(f'\n❌ Teste de login falhou')
