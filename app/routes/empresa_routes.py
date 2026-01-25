"""Rotas de empresas/configurações (autenticadas)"""
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app.services.empresa_service import EmpresaService
from app.services.produto_service import ProdutoService
import os

empresa_bp = Blueprint('empresa', __name__)

empresa_service = EmpresaService()
produto_service = ProdutoService()


@empresa_bp.route('/home')
@login_required
def home():
    """Página inicial logada do usuário"""
    empresa_id = current_user.empresa_id
    empresa = empresa_service.obter_empresa(empresa_id)
    
    if not empresa:
        return "Empresa não encontrada", 404
    
    produtos_com_imagens = produto_service.obter_produtos_com_imagens(empresa_id)
    return render_template('home.html', produto=produtos_com_imagens, empresa=empresa)


@empresa_bp.route('/subscribe/<int:empresa_id>', methods=['GET', 'POST'])
@login_required
def subscribe(empresa_id):
    """Rota de assinatura/checkout.

    GET: mostra página de seleção de planos e checkout.
    POST: efetua o 'upgrade' para o plano selecionado.
    """
    if current_user.empresa_id != empresa_id:
        return "Acesso negado", 403

    empresa = empresa_service.obter_empresa(empresa_id)
    if not empresa:
        return "Empresa não encontrada", 404

    if request.method == 'POST':
        plano = request.form.get('plano', 'pro')
        # Validar plano
        if plano not in ['gratis', 'pro', 'premium']:
            plano = 'pro'
        
        # Atualizar plano da empresa
        empresa.plano = plano
        empresa_service.empresa_repo.update(empresa)
        
        return redirect(url_for('empresa.home'))

    # GET: mostra página de checkout
    return render_template('checkout.html', empresa=empresa)


@empresa_bp.route("/config/<int:empresa_id>", methods=["GET", "POST"])
@login_required
def config(empresa_id):
    """Configurações da empresa"""
    if current_user.empresa_id != empresa_id:
        return "Acesso negado", 403
    
    empresa = empresa_service.obter_empresa(empresa_id)
    
    if not empresa:
        return "Empresa não encontrada", 404
    
    if request.method == 'POST':
        # Preparar dados
        dados = {
            'nome_est': request.form.get('nome_est'),
            'cnpj_est': request.form.get('cnpj_est'),
            'whatsapp': request.form.get('whatsapp'),
            'short_description': request.form.get('short_description'),
            'logradouro': request.form.get('logradouro'),
            'bairro': request.form.get('bairro'),
            'cidade': request.form.get('cidade'),
            'estado': request.form.get('estado'),
            'cep': request.form.get('cep'),
            'primary_color': request.form.get('primary_color'),
            'bg_color': request.form.get('bg_color'),
            'text_color': request.form.get('text_color'),
        }
        
        try:
            basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            
            # Processar logo
            logo_file = request.files.get('logo_file')
            if logo_file and logo_file.filename != '':
                logo_path = empresa_service.processar_upload_arquivo(
                    logo_file, 'logo', empresa_id, basedir
                )
                dados['logo_path'] = logo_path
            
            # Processar banner
            banner_file = request.files.get('banner_file')
            if banner_file and banner_file.filename != '':
                banner_path = empresa_service.processar_upload_arquivo(
                    banner_file, 'banner', empresa_id, basedir
                )
                dados['banner_path'] = banner_path
            
            # Atualizar empresa
            resultado = empresa_service.atualizar_configuracoes(empresa_id, dados, basedir)
            
            if resultado['success']:
                return redirect(url_for('empresa.home'))
            else:
                return resultado['message'], 400
        
        except Exception as e:
            return f"Erro ao salvar: {str(e)}", 500
    
    return render_template('config.html', empresa=empresa)
