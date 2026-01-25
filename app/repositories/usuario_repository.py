"""Repository para gerenciar Usuários"""
from app.models import Usuario
from .base_repository import BaseRepository


class UsuarioRepository(BaseRepository):
    """Operações específicas para Usuários"""
    
    def __init__(self):
        super().__init__(Usuario)
    
    def get_by_email(self, email):
        """Retorna um usuário pelo email"""
        return Usuario.query.filter_by(email=email).first()
    
    def email_exists(self, email):
        """Verifica se um email já está registrado"""
        return self.get_by_email(email) is not None
