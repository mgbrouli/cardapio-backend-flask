from model import db, Produtos, Imagens


def create_prod(nome, ingredientes, preco, image_name=None, image_data=None):


    novo_produto = Produtos(nome= nome, ingredientes=ingredientes, preco=preco)
    db.session.add(novo_produto)
    db.session.commit()

    if image_data is not None:
        nova_imagem = Imagens(produto_id=novo_produto.id, image=image_data)
        db.session.add(nova_imagem)
        db.session.commit()

    return {'message':'Produto adicionado com sucesso'}

def get_all_prod():
    lista_produto = Produtos.query.all()

    return lista_produto

def get_all_prod_with_images():
    """Retorna todos os produtos com suas imagens associadas"""
    produtos = Produtos.query.all()
    resultado = []
    
    for produto in produtos:
        imagem = Imagens.query.filter_by(produto_id=produto.id).first()
        resultado.append({
            'produto': produto,
            'imagem': imagem
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
    
def get_all_images(id):
    """Retorna a imagem associada a um produto específico"""
    return Imagens.query.filter_by(produto_id=id).first()
    