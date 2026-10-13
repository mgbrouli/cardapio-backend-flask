"""Serviço para gerenciar Produtos"""
import base64
import logging
from pathlib import Path
from sqlalchemy import update
from app.database import db
from app.models import Empresa
from app.repositories.produto_repository import ProdutoRepository
from app.repositories.imagem_repository import ImagemRepository

logger = logging.getLogger(__name__)


class ProdutoService:
    """Lógica de negócio para Produtos"""
    
    def __init__(self):
        self.produto_repo = ProdutoRepository()
        self.imagem_repo = ImagemRepository()
    
    def criar_produto(self, empresa_id, nome, ingredientes, preco, image_name=None, image_data=None):
        """Cria um novo produto com imagem opcional"""
        try:
            db.session.execute(
                update(Empresa)
                .where(Empresa.id == empresa_id)
                .values(id=Empresa.id)
            )
            empresa = Empresa.query.get(empresa_id)
            if not empresa:
                db.session.rollback()
                return {'success': False, 'message': 'Empresa não encontrada'}

            if empresa.plano not in {"pro", "premium"} and len(
                self.produto_repo.get_by_empresa(empresa_id)
            ) >= 10:
                db.session.rollback()
                return {
                    'success': False,
                    'message': 'O plano grátis permite até 10 produtos. Assine o Pro para cadastrar mais.',
                }

            # Validar preço
            preco = float(preco)
            ingredientes = ingredientes or ""
            
            # Criar produto
            produto = self.produto_repo.create(
                empresa_id=empresa_id,
                nome=nome,
                ingredientes=ingredientes,
                preco=preco
            )
            
            # Criar imagem se fornecida
            if image_data and image_name:
                self.imagem_repo.create(
                    produto_id=produto.id,
                    empresa_id=empresa_id,
                    name=image_name,
                    image=image_data
                )
            
            return {'success': True, 'message': 'Produto adicionado com sucesso', 'produto_id': produto.id}
        
        except ValueError:
            return {'success': False, 'message': 'Preço inválido'}
        except Exception:
            logger.exception("Falha ao criar produto para empresa %s", empresa_id)
            return {'success': False, 'message': 'Erro ao criar produto'}
    
    def obter_produtos_com_imagens(self, empresa_id):
        """Retorna todos os produtos de uma empresa com suas imagens em base64"""
        produtos = self.produto_repo.get_by_empresa(empresa_id)
        resultado = []
        
        for produto in produtos:
            imagem = self.imagem_repo.get_by_produto(produto.id)
            
            img_base64 = None
            img_mime = "image/jpeg"
            if imagem and imagem.image:
                img_base64 = base64.b64encode(imagem.image).decode('utf-8')
                img_mime = {
                    ".png": "image/png",
                    ".webp": "image/webp",
                    ".avif": "image/avif",
                }.get(Path(imagem.name).suffix.lower(), "image/jpeg")
            
            resultado.append({
                'produto': produto,
                'imagem': img_base64,
                'imagem_mime': img_mime,
            })
        
        return resultado
    
    def atualizar_produto(self, produto_id, nome, ingredientes, preco, image_name=None, image_data=None):
        """Atualiza um produto existente"""
        try:
            preco = float(preco)
            ingredientes = ingredientes or ""
            produto = self.produto_repo.get_by_id(produto_id)
            
            if not produto:
                return {'success': False, 'message': 'Produto não encontrado'}
            
            # Atualizar dados do produto
            self.produto_repo.update(
                produto,
                nome=nome,
                ingredientes=ingredientes,
                preco=preco
            )
            
            # Atualizar ou criar imagem
            if image_data and image_name:
                imagem = self.imagem_repo.get_by_produto(produto_id)
                if imagem:
                    self.imagem_repo.update(
                        imagem,
                        name=image_name,
                        image=image_data
                    )
                else:
                    self.imagem_repo.create(
                        produto_id=produto_id,
                        empresa_id=produto.empresa_id,
                        name=image_name,
                        image=image_data
                    )
            
            return {'success': True, 'message': 'Produto atualizado com sucesso'}
        
        except ValueError:
            return {'success': False, 'message': 'Preço inválido'}
        except Exception:
            logger.exception("Falha ao atualizar produto %s", produto_id)
            return {'success': False, 'message': 'Erro ao atualizar produto'}
    
    def deletar_produto(self, produto_id):
        """Deleta um produto"""
        try:
            if self.produto_repo.delete_by_id(produto_id):
                return {'success': True, 'message': 'Produto deletado com sucesso'}
            return {'success': False, 'message': 'Produto não encontrado'}
        except Exception:
            logger.exception("Falha ao deletar produto %s", produto_id)
            return {'success': False, 'message': 'Erro ao deletar produto'}
