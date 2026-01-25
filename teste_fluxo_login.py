#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para testar fluxo completo de login"""

from app import create_app

app = create_app()
client = app.test_client()

print('='*60)
print('🧪 TESTE DE LOGIN COMPLETO')
print('='*60)

# 1. Teste GET /login
print('\n1️⃣  GET /login')
response = client.get('/login')
print(f'   Status: {response.status_code}')
print(f'   Template renderizado: {"landing.html" in response.get_data(as_text=True)}')

# 2. Teste POST /login com credenciais corretas
print('\n2️⃣  POST /login (credenciais corretas)')
response = client.post('/login', data={
    'email': 'teste@teste.com',
    'senha': '123456'
}, follow_redirects=False)  # Não seguir redirects para ver para onde vai
print(f'   Status: {response.status_code}')
print(f'   Localização do redirect: {response.headers.get("Location", "Nenhum")}')

# 3. Teste POST /login com follow_redirects=True
print('\n3️⃣  POST /login (seguindo redirects)')
response = client.post('/login', data={
    'email': 'teste@teste.com',
    'senha': '123456'
}, follow_redirects=True)
print(f'   Status final: {response.status_code}')
print(f'   Total de redirects: {len(response.history)}')
print(f'   URL final: {response.request.path if hasattr(response, "request") else "N/A"}')

# Verificar se chegou na página de empresa
html = response.get_data(as_text=True)
if 'Gestão de Cardápio' in html:
    print('   ✅ Chegou na página de empresa!')
elif 'Acesse seu Painel' in html:
    print('   ❌ Voltou para login (modal)')
    # Verificar se tem aviso de erro
    if 'alert-danger' in html:
        print('   ⚠️  Há um alerta de erro na página')
else:
    print(f'   ❌ Chegou em uma página inesperada')
    # Procurar por pistas
    if 'landing' in html.lower():
        print('   ℹ️  Parece ser a página landing')
    elif 'home' in html.lower():
        print('   ℹ️  Parece ser a página home')

# 4. Teste POST /login com credenciais incorretas
print('\n4️⃣  POST /login (credenciais incorretas)')
response = client.post('/login', data={
    'email': 'teste@teste.com',
    'senha': 'senhaerrada'
}, follow_redirects=True)
print(f'   Status: {response.status_code}')
html = response.get_data(as_text=True)
if 'alert-danger' in html:
    print('   ✅ Mostra aviso de erro')
    if 'Senha incorreta' in html:
        print('   ✅ Mensagem de erro: "Senha incorreta"')
else:
    print('   ❌ Não mostra aviso de erro')

print('\n' + '='*60)
