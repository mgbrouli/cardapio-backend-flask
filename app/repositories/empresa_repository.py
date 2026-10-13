"""Repository para gerenciar Empresas"""
from sqlalchemy import func

from app.models import Usuario
from app.models import Empresa
from .base_repository import BaseRepository


class EmpresaRepository(BaseRepository):
    """Operações específicas para Empresas"""
    
    def __init__(self):
        super().__init__(Empresa)
    
    def get_ativa_by_id(self, empresa_id):
        """Retorna uma empresa ativa pelo ID"""
        return Empresa.query.filter_by(id=empresa_id, ativo=True).first()

    def get_ativas(self, limit=12, excluded_owner_emails=()):
        """Retorna empresas ativas para a vitrine pública."""
        query = Empresa.query.filter_by(ativo=True)
        normalized_emails = [
            email.strip().casefold()
            for email in excluded_owner_emails
            if isinstance(email, str) and email.strip()
        ]
        if normalized_emails:
            admin_company_ids = (
                Usuario.query.with_entities(Usuario.empresa_id)
                .filter(
                    Usuario.empresa_id.isnot(None),
                    func.lower(Usuario.email).in_(normalized_emails),
                )
            )
            query = query.filter(~Empresa.id.in_(admin_company_ids))
        return query.order_by(Empresa.id.desc()).limit(limit).all()
