"""Repository para gerenciar Produtos"""
from app.models import Produtos, db
from .base_repository import BaseRepository


class ProdutoRepository(BaseRepository):
    """Operações específicas para Produtos"""
    
    def __init__(self):
        super().__init__(Produtos)
    
    def get_by_empresa(self, empresa_id):
        """Retorna todos os produtos de uma empresa"""
        return Produtos.query.filter_by(empresa_id=empresa_id).all()
    
    def get_by_id_and_empresa(self, produto_id, empresa_id):
        """Retorna um produto específico de uma empresa"""
        return Produtos.query.filter_by(id=produto_id, empresa_id=empresa_id).first()
    
    def delete_by_id(self, produto_id):
        """Deleta um produto pelo ID"""
        try:
            produto = self.get_by_id(produto_id)
            if produto:
                db.session.delete(produto)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            raise e
