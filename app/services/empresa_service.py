"""Serviço para gerenciar Empresas"""
import os
import time
from flask import url_for
from app.repositories.empresa_repository import EmpresaRepository


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
    
    def atualizar_configuracoes(self, empresa_id, dados, basedir):
        """Atualiza as configurações de uma empresa"""
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
            
            self.empresa_repo.update(empresa, **{})
            
            return {'success': True, 'message': 'Configurações atualizadas com sucesso'}
        
        except Exception as e:
            return {'success': False, 'message': f'Erro ao atualizar configurações: {str(e)}'}
    
    def processar_upload_arquivo(self, arquivo, tipo, empresa_id, basedir):
        """Processa upload de arquivos (logo/banner)"""
        if not arquivo or arquivo.filename == '':
            return None
        
        try:
            uploads_dir = os.path.join(basedir, 'static', 'uploads')
            os.makedirs(uploads_dir, exist_ok=True)
            
            # Gerar nome único
            timestamp = int(time.time())
            filename = f'{tipo}_{empresa_id}_{timestamp}_{arquivo.filename}'
            filepath = os.path.join(uploads_dir, filename)
            
            arquivo.save(filepath)
            return url_for('static', filename=f'uploads/{filename}')
        
        except Exception as e:
            raise Exception(f'Erro ao processar arquivo: {str(e)}')
