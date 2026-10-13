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

# Verificar usuários sem imprimir hashes de senha
print('\n👤 Usuários no banco:')
try:
    cursor.execute('SELECT id, email, empresa_id FROM usuario')
    usuarios = cursor.fetchall()
    print(f'   Total: {len(usuarios)}')
    for u in usuarios:
        print(f'   - ID: {u[0]}, Email: {u[1]}, Empresa: {u[3]}')
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

conn.close()
