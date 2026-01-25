"""
Arquivo de compatibilidade para o modelo antigo.
Importa todos os modelos de app.models para manter compatibilidade backward.

NOVO: Use app.models ao invés deste arquivo
from app.models import db, Produtos, Imagens, Empresa, Usuario
"""

from app.models import db, Produtos, Imagens, Empresa, Usuario

__all__ = ['db', 'Produtos', 'Imagens', 'Empresa', 'Usuario']
