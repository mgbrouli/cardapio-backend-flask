#!/usr/bin/env python
"""Redefine uma senha usando Argon2 sem exibir ou armazenar credenciais."""

from getpass import getpass

from app import create_app, db
from app.models import Usuario
from app.services.auth_service import password_hasher

create_app()
email = input("E-mail da conta: ").strip()
new_password = getpass("Nova senha: ")
if not new_password or new_password != getpass("Repita a nova senha: "):
    raise SystemExit("As senhas estão vazias ou não coincidem.")

usuario = Usuario.query.filter_by(email=email).first()
if usuario is None:
    raise SystemExit("Usuário não encontrado.")

usuario.senha = password_hasher.hash(new_password)
db.session.commit()
print("Senha atualizada com Argon2.")
