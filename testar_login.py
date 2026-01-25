#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para testar login"""

from app import create_app
from app.services.auth_service import AuthService

app = create_app()
with app.app_context():
    service = AuthService()
    
    # Listar usuários disponíveis
    print('📋 Usuários no banco:')
    usuarios = service.usuario_repo.get_all()
    for u in usuarios:
        print(f'   - {u.email}')
    
    print('\n' + '='*60)
    
    # Testar com cada usuário
    for usuario in usuarios:
        print(f'\n🔐 Testando login: {usuario.email}')
        
        # Tentar com senha "123456"
        result = service.validar_credenciais(usuario.email, '123456')
        print(f'   Senha "123456": {result["success"]}')
        if not result['success']:
            print(f'   Mensagem: {result["message"]}')
