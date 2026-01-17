from model import db, Produtos


def create_prod(nome, ingredientes, preco):

    novo_produto = Produtos(nome= nome, ingredientes=ingredientes, preco=preco)
    db.session.add(novo_produto)
    db.session.commit()

    return {'message':'Produto adicionado com sucesso'}

def get_all_prod():
    lista_produto = Produtos.query.all()

    return lista_produto

def delete_prod(id):
    produto = Produtos.query.get_or_404(id)

    try:
        db.session.delete(produto)
        db.session.commit()

        return '', 204
    except:
        return 'Erro', 500