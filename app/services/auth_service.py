"""Serviço para autenticação e gerenciar usuários"""
from werkzeug.security import generate_password_hash, check_password_hash
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.empresa_repository import EmpresaRepository
from app.models import db, Usuario, Empresa


class AuthService:
    """Lógica de autenticação e gerencimento de usuários"""
    
    def __init__(self):
        self.usuario_repo = UsuarioRepository()
        self.empresa_repo = EmpresaRepository()
    
    def registrar_usuario(self, email, senha, nome_loja, whatsapp):
        """Registra um novo usuário com sua empresa"""
        try:
            # Validar se email já existe
            if self.usuario_repo.email_exists(email):
                return {'success': False, 'message': 'Este e-mail já está cadastrado'}
            
            # Criar empresa
            empresa = self.empresa_repo.create(
                name_est=nome_loja,
                whatsapp=whatsapp
            )
            
            # Criar usuário
            hash_senha = generate_password_hash(senha)
            usuario = self.usuario_repo.create(
                email=email,
                senha=hash_senha,
                empresa_id=empresa.id
            )
            
            return {
                'success': True,
                'message': 'Cadastro realizado com sucesso',
                'usuario_id': usuario.id,
                'empresa_id': empresa.id
            }
        
        except Exception as e:
            return {'success': False, 'message': f'Erro ao registrar: {str(e)}'}
    
    def validar_credenciais(self, email, senha):
        """Valida as credenciais do usuário"""
        usuario = self.usuario_repo.get_by_email(email)
        
        if not usuario:
            return {'success': False, 'message': 'Usuário não encontrado'}
        
        if not check_password_hash(usuario.senha, senha):
            return {'success': False, 'message': 'Senha incorreta'}
        
        return {
            'success': True,
            'message': 'Login realizado com sucesso',
            'usuario': usuario
        }
    
    def obter_usuario(self, usuario_id):
        """Obtém um usuário pelo ID"""
        return self.usuario_repo.get_by_id(usuario_id)
