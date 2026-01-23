from model import db, Produtos, Imagens
import base64

def create_prod(empresa_id ,nome, ingredientes, preco, image_name=None, image_data=None):

    novo_produto = Produtos(nome=nome, ingredientes=ingredientes, preco=preco, empresa_id=empresa_id)
    db.session.add(novo_produto)
    db.session.commit()

    if image_data is not None and image_name is not None:
        nova_imagem = Imagens(produto_id=novo_produto.id, empresa_id=empresa_id, name=image_name, image=image_data)
        db.session.add(nova_imagem)
        db.session.commit()

    return {'message': 'Produto adicionado com sucesso'}

def get_all_prod():
    lista_produto = Produtos.query.all()

    return lista_produto

def get_all_prod_with_images(empresa_id):
    """Retorna todos os produtos com suas imagens associadas"""
    produtos = Produtos.query.filter_by(empresa_id).all()
    resultado = []
    
    for produto in produtos:
        imagem = Imagens.query.filter_by(produto_id=produto.id, empresa_id=empresa_id).first()

        img_base64 = None
        if imagem and imagem.image:
            img_base64 = base64.b64encode(imagem.image).decode('utf-8')

        resultado.append({
            'produto': produto,
            'imagem': img_base64
        })
    
    return resultado

def delete_prod(id):
    produto = Produtos.query.get_or_404(id)

    try:
        db.session.delete(produto)
        db.session.commit()

        return '', 204
    except:
        return 'Erro', 500

def update_prod(id, nome, ingredientes, preco, image_name=None, image_data=None):
    """Atualiza um produto existente"""
    produto = Produtos.query.get_or_404(id)
    
    produto.nome = nome
    produto.ingredientes = ingredientes
    produto.preco = preco
    db.session.commit()
    
    # Se uma nova imagem foi enviada, atualizar ou criar
    if image_data is not None and image_name is not None:
        imagem = Imagens.query.filter_by(produto_id=id).first()
        if imagem:
            imagem.name = image_name
            imagem.image = image_data
            db.session.commit()
        else:
            nova_imagem = Imagens(produto_id=id, name=image_name, image=image_data)
            db.session.add(nova_imagem)
            db.session.commit()
    
    return {'message': 'Produto atualizado com sucesso'}
    
    
def get_all_images(id):
    """Retorna a imagem associada a um produto específico"""
    return Imagens.query.filter_by(produto_id=id).first()
    