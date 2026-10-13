"""Serviço para gerenciar Empresas"""
import logging
import os
from pathlib import Path
from uuid import uuid4
from werkzeug.utils import secure_filename
from app.repositories.empresa_repository import EmpresaRepository
from app.utils.image_utils import validate_image_content

logger = logging.getLogger(__name__)


class EmpresaService:
    """Lógica de negócio para Empresas"""
    
    def __init__(self):
        self.empresa_repo = EmpresaRepository()
    
    def obter_empresa(self, empresa_id):
        """Obtém uma empresa pelo ID"""
        return self.empresa_repo.get_by_id(empresa_id)
    
    def obter_empresa_ativa(self, empresa_id):
        """Obtém uma empresa ativa pelo ID"""
        return self.empresa_repo.get_ativa_by_id(empresa_id)

    def listar_empresas_publicas(self, limite=12, emails_privados=()):
        """Lista empresas ativas para exibição na página inicial."""
        return self.empresa_repo.get_ativas(
            limit=limite, excluded_owner_emails=emails_privados
        )
    
    def atualizar_configuracoes(self, empresa_id, dados, _basedir):
        """Atualiza as configurações de uma empresa"""
        _ = _basedir
        try:
            empresa = self.empresa_repo.get_by_id(empresa_id)
            
            if not empresa:
                return {'success': False, 'message': 'Empresa não encontrada'}
            
            # Atualizar dados gerais
            if 'nome_est' in dados:
                empresa.name_est = dados['nome_est']
            if 'cnpj_est' in dados:
                empresa.cnpj_est = dados['cnpj_est']
            if 'whatsapp' in dados:
                empresa.whatsapp = dados['whatsapp']
            if 'short_description' in dados:
                empresa.short_description = dados['short_description']
            
            # Atualizar endereço
            if 'logradouro' in dados:
                empresa.logradouro = dados['logradouro']
            if 'bairro' in dados:
                empresa.bairro = dados['bairro']
            if 'cidade' in dados:
                empresa.cidade = dados['cidade']
            if 'estado' in dados:
                empresa.estado = dados['estado']
            if 'cep' in dados:
                empresa.cep = dados['cep']
            
            # Atualizar cores
            if 'primary_color' in dados:
                empresa.primary_color = dados['primary_color']
            if 'bg_color' in dados:
                empresa.bg_color = dados['bg_color']
            if 'text_color' in dados:
                empresa.text_color = dados['text_color']
            
            # Atualizar logos/banners
            if 'logo_path' in dados:
                empresa.logo_path = dados['logo_path']
            if 'banner_path' in dados:
                empresa.banner_path = dados['banner_path']
            
            # Fazer commit das alterações
            self.empresa_repo.update(empresa)
            
            return {'success': True, 'message': 'Configurações atualizadas com sucesso'}
        
        except Exception:
            logger.exception("Falha ao atualizar configurações da empresa %s", empresa_id)
            return {'success': False, 'message': 'Erro ao atualizar configurações'}
    
    def processar_upload_arquivo(self, arquivo, tipo, empresa_id, basedir):
        """Processa upload de arquivos (logo/banner)"""
        if not arquivo or not arquivo.filename:
            return None

        if tipo not in {"logo", "banner"}:
            raise ValueError("Tipo de imagem inválido")

        extension = Path(secure_filename(arquivo.filename)).suffix.lower()
        content = arquivo.file.read(5 * 1024 * 1024 + 1)
        validate_image_content(arquivo.filename, content)

        uploads_dir = os.path.join(basedir, "static", "uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        filename = f"{tipo}_{empresa_id}_{uuid4().hex}{extension}"
        filepath = os.path.join(uploads_dir, filename)
        with open(filepath, "wb") as destination:
            destination.write(content)
        return f"/static/uploads/{filename}"

    def assinar_empresa(self, empresa_id):
        """Marca a empresa como assinante premium (placeholder)."""
        try:
            empresa = self.empresa_repo.get_by_id(empresa_id)
            if not empresa:
                return {'success': False, 'message': 'Empresa não encontrada'}

            empresa.plano = 'premium'
            self.empresa_repo.update(empresa)
            return {'success': True, 'message': 'Empresa atualizada para Premium'}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao assinar: {str(e)}'}
