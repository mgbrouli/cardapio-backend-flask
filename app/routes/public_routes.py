"""Rotas públicas (sem autenticação)"""
from flask import Blueprint, render_template
from app.services.produto_service import ProdutoService
from app.services.empresa_service import EmpresaService

public_bp = Blueprint('public', __name__)

produto_service = ProdutoService()
empresa_service = EmpresaService()


@public_bp.route('/')
def landing():
    """Página de landing"""
    return render_template('landing.html')


@public_bp.route('/<int:empresa_id>', methods=['GET'])
def index(empresa_id):
    """Exibe cardápio de uma empresa"""
    empresa = empresa_service.obter_empresa_ativa(empresa_id)
    
    if not empresa:
        return "Este cardápio está temporariamente suspenso. Entre em contato com o administrador.", 403
    
    produtos_com_imagens = produto_service.obter_produtos_com_imagens(empresa_id)
    return render_template('index.html', produto=produtos_com_imagens, empresa=empresa)
