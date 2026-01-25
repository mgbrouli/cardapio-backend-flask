#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para resetar e criar dados de teste corretamente"""

from app import create_app, db
from app.models import Usuario, Empresa
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    try:
        # Remover usuário teste anterior se existir
        Usuario.query.filter_by(email='teste@teste.com').delete()
        db.session.commit()
        print("✅ Usuário teste anterior removido")
        
        # Obter a empresa existente
        empresa = Empresa.query.first()
        if not empresa:
            print("❌ Nenhuma empresa encontrada!")
            exit(1)
        
        print(f"✅ Usando empresa: {empresa.name_est} (ID: {empresa.id})")
        
        # Criar novo usuário de teste
        usuario_teste = Usuario(
            email='teste@teste.com',
            senha=generate_password_hash('123456'),
            empresa_id=empresa.id
        )
        db.session.add(usuario_teste)
        db.session.commit()
        
        print("\n✅ Usuário de teste criado:")
        print(f"   📧 Email: teste@teste.com")
        print(f"   🔐 Senha: 123456")
        print(f"   🏢 Empresa: {empresa.name_est}")
        
        # Verificar que foi salvo
        usuario_verificacao = Usuario.query.filter_by(email='teste@teste.com').first()
        if usuario_verificacao:
            print("\n✅ Usuário verificado no banco de dados!")
        else:
            print("\n❌ Erro: usuário não foi salvo!")
        
        # Listar todos os usuários
        print("\n📋 Usuários no banco:")
        todos_usuarios = Usuario.query.all()
        for u in todos_usuarios:
            print(f"   - {u.email}")
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
