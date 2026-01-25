#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para criar dados de teste"""

from app import create_app, db
from app.models import Usuario, Empresa
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    try:
        # Verificar se há empresa
        empresa = Empresa.query.first()
        if not empresa:
            print("📦 Criando empresa de teste...")
            empresa = Empresa(
                name_est='Pizzaria Teste',
                whatsapp='11999999999',
                primary_color='#0d6efd',
                bg_color='#f8f9fa',
                text_color='#333'
            )
            db.session.add(empresa)
            db.session.commit()
            print(f"✅ Empresa criada com ID: {empresa.id}")
        else:
            print(f"✅ Empresa encontrada: {empresa.name_est} (ID: {empresa.id})")
        
        # Verificar se há usuário de teste
        usuario = Usuario.query.filter_by(email='teste@teste.com').first()
        if not usuario:
            print("👤 Criando usuário de teste...")
            usuario = Usuario(
                email='teste@teste.com',
                senha=generate_password_hash('123456'),
                empresa_id=empresa.id
            )
            db.session.add(usuario)
            db.session.commit()
            print(f"✅ Usuário criado!")
            print(f"   Email: teste@teste.com")
            print(f"   Senha: 123456")
        else:
            print(f"✅ Usuário já existe: teste@teste.com")
        
        print("\n✅ Dados de teste prontos!")
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
