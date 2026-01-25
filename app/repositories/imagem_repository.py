"""Repository para gerenciar Imagens"""
from app.models import Imagens, db
from .base_repository import BaseRepository


class ImagemRepository(BaseRepository):
    """Operações específicas para Imagens"""
    
    def __init__(self):
        super().__init__(Imagens)
    
    def get_by_produto(self, produto_id):
        """Retorna a imagem de um produto"""
        return Imagens.query.filter_by(produto_id=produto_id).first()
    
    def get_by_produto_and_empresa(self, produto_id, empresa_id):
        """Retorna a imagem de um produto específico de uma empresa"""
        return Imagens.query.filter_by(produto_id=produto_id, empresa_id=empresa_id).first()
    
    def delete_by_produto(self, produto_id):
        """Deleta a imagem de um produto"""
        try:
            imagem = self.get_by_produto(produto_id)
            if imagem:
                db.session.delete(imagem)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            raise e
