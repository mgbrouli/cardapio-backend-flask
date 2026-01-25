"""
Arquivo de compatibilidade para o controller antigo.
Importa e re-exporta funções do novo ProdutoService para manter compatibilidade backward.

NOVO: Use app.services.produto_service ao invés deste arquivo
from app.services.produto_service import ProdutoService
"""

from app.services.produto_service import ProdutoService
from app.repositories.imagem_repository import ImagemRepository

# Instanciar serviço
_produto_service = ProdutoService()
_imagem_repo = ImagemRepository()


# Funções de compatibilidade
def create_prod(empresa_id, nome, ingredientes, preco, image_name=None, image_data=None):
    """Compatibilidade: create_prod → ProdutoService.criar_produto"""
    resultado = _produto_service.criar_produto(
        empresa_id=empresa_id,
        nome=nome,
        ingredientes=ingredientes,
        preco=preco,
        image_name=image_name,
        image_data=image_data
    )
    return resultado


def get_all_prod():
    """Compatibilidade: get_all_prod → deprecated"""
    from app.models import Produtos
    return Produtos.query.all()


def get_all_prod_with_images(empresa_id):
    """Compatibilidade: get_all_prod_with_images → ProdutoService.obter_produtos_com_imagens"""
    return _produto_service.obter_produtos_com_imagens(empresa_id)


def delete_prod(id):
    """Compatibilidade: delete_prod → ProdutoService.deletar_produto"""
    resultado = _produto_service.deletar_produto(id)
    
    if resultado['success']:
        return '', 204
    else:
        return resultado['message'], 500


def update_prod(id, nome, ingredientes, preco, image_name=None, image_data=None):
    """Compatibilidade: update_prod → ProdutoService.atualizar_produto"""
    return _produto_service.atualizar_produto(
        produto_id=id,
        nome=nome,
        ingredientes=ingredientes,
        preco=preco,
        image_name=image_name,
        image_data=image_data
    )


def get_all_images(id):
    """Compatibilidade: get_all_images → ImagemRepository.get_by_produto"""
    return _imagem_repo.get_by_produto(id)


__all__ = [
    'create_prod',
    'get_all_prod',
    'get_all_prod_with_images',
    'delete_prod',
    'update_prod',
    'get_all_images'
]
