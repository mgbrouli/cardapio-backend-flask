#!/usr/bin/env python
"""Lista os registros atuais sem imprimir hashes ou testar senhas conhecidas."""

from app import create_app
from app.models import Empresa, Usuario

create_app()

print("VERIFICAÇÃO DO BANCO")
empresas = Empresa.query.all()
usuarios = Usuario.query.all()
print(f"Empresas: {len(empresas)}")
for empresa in empresas:
    print(f"  {empresa.id}: {empresa.name_est}")
print(f"Usuários: {len(usuarios)}")
for usuario in usuarios:
    print(f"  {usuario.id}: {usuario.email} (empresa_id: {usuario.empresa_id})")
