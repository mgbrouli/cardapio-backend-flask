"""Repository para gerenciar Empresas"""
from app.models import Empresa
from .base_repository import BaseRepository


class EmpresaRepository(BaseRepository):
    """Operações específicas para Empresas"""
    
    def __init__(self):
        super().__init__(Empresa)
    
    def get_ativa_by_id(self, empresa_id):
        """Retorna uma empresa ativa pelo ID"""
        return Empresa.query.filter_by(id=empresa_id, ativo=True).first()

    def get_ativas(self, limit=12):
        """Retorna empresas ativas para a vitrine pública."""
        return (
            Empresa.query.filter_by(ativo=True)
            .order_by(Empresa.id.desc())
            .limit(limit)
            .all()
        )
