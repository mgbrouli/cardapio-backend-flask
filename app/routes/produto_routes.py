"""Rotas de produtos (autenticadas)"""
from flask import Blueprint, request, redirect, url_for
from flask_login import login_required, current_user
from app.services.produto_service import ProdutoService

produto_bp = Blueprint('produto', __name__, url_prefix='/produto')

produto_service = ProdutoService()


@produto_bp.route('/add/<int:empresa_id>', methods=['POST'])
@login_required
def add_produto(empresa_id):
    """Adiciona um novo produto"""
    if current_user.empresa_id != empresa_id:
        return "Acesso negado", 403
    
    nome = request.form.get('nome')
    ingredientes = request.form.get('ingredientes')
    preco = request.form.get('preco')
    
    # Processar imagem
    imagem_arquivo = request.files.get('image')
    nome_imagem = None
    imagem_dados = None
    
    if imagem_arquivo:
        nome_imagem = imagem_arquivo.filename
        imagem_dados = imagem_arquivo.read()
    
    resultado = produto_service.criar_produto(
        empresa_id=empresa_id,
        nome=nome,
        ingredientes=ingredientes,
        preco=preco,
        image_name=nome_imagem,
        image_data=imagem_dados
    )
    
    if resultado['success']:
        return redirect(url_for('empresa.home'))
    else:
        return resultado['message'], 400


@produto_bp.route('/edit/<int:produto_id>', methods=['POST'])
@login_required
def edit_produto(produto_id):
    """Edita um produto existente"""
    nome = request.form.get('nome')
    ingredientes = request.form.get('ingredientes')
    preco = request.form.get('preco')
    
    # Processar imagem (opcional)
    imagem_arquivo = request.files.get('imagem')
    nome_imagem = None
    imagem_dados = None
    
    if imagem_arquivo:
        nome_imagem = imagem_arquivo.filename
        imagem_dados = imagem_arquivo.read()
    
    resultado = produto_service.atualizar_produto(
        produto_id=produto_id,
        nome=nome,
        ingredientes=ingredientes,
        preco=preco,
        image_name=nome_imagem,
        image_data=imagem_dados
    )
    
    if resultado['success']:
        return redirect(url_for('empresa.home'))
    else:
        return resultado['message'], 400


@produto_bp.route('/delete/<int:produto_id>', methods=['DELETE'])
@login_required
def delete_produto(produto_id):
    """Deleta um produto"""
    resultado = produto_service.deletar_produto(produto_id)
    
    if resultado['success']:
        return '', 204
    else:
        return resultado['message'], 400
