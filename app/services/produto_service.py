"""Serviço para gerenciar Produtos"""
import base64
from app.repositories.produto_repository import ProdutoRepository
from app.repositories.imagem_repository import ImagemRepository


class ProdutoService:
    """Lógica de negócio para Produtos"""
    
    def __init__(self):
        self.produto_repo = ProdutoRepository()
        self.imagem_repo = ImagemRepository()
    
    def criar_produto(self, empresa_id, nome, ingredientes, preco, image_name=None, image_data=None):
        """Cria um novo produto com imagem opcional"""
        try:
            # Validar preço
            preco = float(preco)
            
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
        except Exception as e:
            return {'success': False, 'message': f'Erro ao criar produto: {str(e)}'}
    
    def obter_produtos_com_imagens(self, empresa_id):
        """Retorna todos os produtos de uma empresa com suas imagens em base64"""
        produtos = self.produto_repo.get_by_empresa(empresa_id)
        resultado = []
        
        for produto in produtos:
            imagem = self.imagem_repo.get_by_produto(produto.id)
            
            img_base64 = None
            if imagem and imagem.image:
                img_base64 = base64.b64encode(imagem.image).decode('utf-8')
            
            resultado.append({
                'produto': produto,
                'imagem': img_base64
            })
        
        return resultado
    
    def atualizar_produto(self, produto_id, nome, ingredientes, preco, image_name=None, image_data=None):
        """Atualiza um produto existente"""
        try:
            preco = float(preco)
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
        except Exception as e:
            return {'success': False, 'message': f'Erro ao atualizar produto: {str(e)}'}
    
    def deletar_produto(self, produto_id):
        """Deleta um produto"""
        try:
            if self.produto_repo.delete_by_id(produto_id):
                return {'success': True, 'message': 'Produto deletado com sucesso'}
            return {'success': False, 'message': 'Produto não encontrado'}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao deletar produto: {str(e)}'}
