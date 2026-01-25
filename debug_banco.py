#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para verificar conteúdo do banco de dados"""

import sqlite3

# Conectar ao banco de dados
conn = sqlite3.connect('banco.db')
cursor = conn.cursor()

# Ver tabelas
print('📋 Tabelas no banco:')
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(f'   - {table[0]}')

# Ver conteúdo da tabela usuario
print('\n👤 Usuários no banco:')
try:
    cursor.execute('SELECT id, email, senha, empresa_id FROM usuario')
    usuarios = cursor.fetchall()
    print(f'   Total: {len(usuarios)}')
    for u in usuarios:
        print(f'   - ID: {u[0]}, Email: {u[1]}, Empresa: {u[3]}')
        print(f'     Senha (hash): {u[2][:50]}...')
except Exception as e:
    print(f'   Erro: {e}')

# Ver conteúdo da tabela empresa
print('\n🏢 Empresas no banco:')
try:
    cursor.execute('SELECT id, name_est FROM empresa')
    empresas = cursor.fetchall()
    print(f'   Total: {len(empresas)}')
    for e in empresas:
        print(f'   - ID: {e[0]}, Nome: {e[1]}')
except Exception as e:
    print(f'   Erro: {e}')

print('\n' + '='*60)

# Testar os dados que estão lá
print('\n🔐 Testando autenticação com dados do banco:')
from app import create_app, db
from app.services.auth_service import AuthService

app = create_app()
with app.app_context():
    service = AuthService()
    
    # Pegar todos os usuários
    usuarios_db = service.usuario_repo.get_all()
    print(f'   Usuários encontrados (via repository): {len(usuarios_db)}')
    
    for u in usuarios_db:
        print(f'\n   Testando: {u.email}')
        
        # Tentar validar com senha "123456"
        resultado = service.validar_credenciais(u.email, '123456')
        print(f'   - Validação com "123456": {resultado["success"]}')
        
        # Se falhou, mostrar mensagem
        if not resultado['success']:
            print(f'     Mensagem: {resultado["message"]}')

conn.close()
