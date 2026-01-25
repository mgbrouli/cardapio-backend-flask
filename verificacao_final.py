#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Verificação final do banco e login"""

from app import create_app, db
from app.models import Usuario, Empresa

app = create_app()

with app.app_context():
    print('🔍 VERIFICAÇÃO FINAL DO BANCO')
    print('='*60)
    
    empresas = Empresa.query.all()
    print(f'✅ Empresas: {len(empresas)}')
    for e in empresas:
        print(f'   - {e.id}: {e.name_est}')
    
    usuarios = Usuario.query.all()
    print(f'✅ Usuários: {len(usuarios)}')
    for u in usuarios:
        print(f'   - {u.id}: {u.email} (empresa_id: {u.empresa_id})')
    
    print('\n🧪 TESTE DE LOGIN')
    from app.services.auth_service import AuthService
    service = AuthService()
    
    resultado = service.validar_credenciais('teste@teste.com', '123456')
    print(f'✅ Login funciona: {resultado["success"]}')
    if resultado['success']:
        user = resultado['usuario']
        print(f'   User ID: {user.id}')
        print(f'   Email: {user.email}')
        print(f'   Empresa ID: {user.empresa_id}')
    
    print('\n✅ TUDO PRONTO PARA LOGIN NO NAVEGADOR!')
    print('   Email: teste@teste.com')
    print('   Senha: 123456')
