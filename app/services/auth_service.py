"""Serviço de autenticação e gerenciamento de usuários."""

import hmac

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from werkzeug.security import check_password_hash

from app.repositories.empresa_repository import EmpresaRepository
from app.repositories.usuario_repository import UsuarioRepository

password_hasher = PasswordHasher()


class AuthService:
    """Lógica de autenticação e gerenciamento de usuários."""

    def __init__(self):
        self.usuario_repo = UsuarioRepository()
        self.empresa_repo = EmpresaRepository()

    def registrar_usuario(self, email, senha, nome_loja, whatsapp):
        """Registra um usuário e sua empresa com senha em Argon2."""
        try:
            if self.usuario_repo.email_exists(email):
                return {"success": False, "message": "Este e-mail já está cadastrado"}

            empresa = self.empresa_repo.create(name_est=nome_loja, whatsapp=whatsapp)
            usuario = self.usuario_repo.create(
                email=email,
                senha=password_hasher.hash(senha),
                empresa_id=empresa.id,
            )
            return {
                "success": True,
                "message": "Cadastro realizado com sucesso",
                "usuario_id": usuario.id,
                "empresa_id": empresa.id,
            }
        except Exception as exc:
            return {"success": False, "message": f"Erro ao registrar: {exc}"}

    def validar_credenciais(self, email, senha):
        """Valida credenciais e atualiza hashes legados para Argon2."""
        usuario = self.usuario_repo.get_by_email(email)
        if not usuario:
            return {"success": False, "message": "Usuário não encontrado"}

        senha_atual = usuario.senha
        if senha_atual.startswith("$argon2"):
            try:
                password_hasher.verify(senha_atual, senha)
            except (VerifyMismatchError, VerificationError, InvalidHashError, TypeError):
                return {"success": False, "message": "Senha incorreta"}
            if password_hasher.check_needs_rehash(senha_atual):
                self.usuario_repo.update(usuario, senha=password_hasher.hash(senha))
        else:
            try:
                senha_valida = check_password_hash(senha_atual, senha)
            except (TypeError, ValueError):
                senha_valida = False
            if not senha_valida and not senha_atual.startswith(
                ("pbkdf2:", "scrypt:", "sha1$", "md5$")
            ):
                senha_valida = hmac.compare_digest(
                    senha_atual.encode("utf-8"), senha.encode("utf-8")
                )
            if not senha_valida:
                return {"success": False, "message": "Senha incorreta"}
            self.usuario_repo.update(usuario, senha=password_hasher.hash(senha))

        return {
            "success": True,
            "message": "Login realizado com sucesso",
            "usuario": usuario,
        }

    def obter_usuario(self, usuario_id):
        """Obtém um usuário pelo ID."""
        return self.usuario_repo.get_by_id(usuario_id)
