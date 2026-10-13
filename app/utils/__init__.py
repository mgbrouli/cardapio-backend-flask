"""Funções utilitárias da aplicação"""

import os
import time


def gerar_nome_arquivo_unico(tipo, empresa_id, filename):
    """
    Gera um nome único para arquivo upload
    
    Args:
        tipo: 'logo', 'banner', 'produto'
        empresa_id: ID da empresa
        filename: Nome original do arquivo
    
    Returns:
        Nome único do arquivo
    """
    timestamp = int(time.time())
    return f'{tipo}_{empresa_id}_{timestamp}_{filename}'


def validar_preco(preco):
    """
    Valida se o preço é um número válido
    
    Args:
        preco: Preço a validar
    
    Returns:
        float: Preço validado
    
    Raises:
        ValueError: Se preço inválido
    """
    try:
        preco = float(preco)
        if preco < 0:
            raise ValueError("Preço não pode ser negativo")
        return preco
    except (ValueError, TypeError):
        raise ValueError("Preço deve ser um número válido")


def criar_diretorio_upload(basedir):
    """
    Cria diretório de uploads se não existir
    
    Args:
        basedir: Diretório base da aplicação
    
    Returns:
        str: Caminho do diretório de uploads
    """
    uploads_dir = os.path.join(basedir, 'static', 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    return uploads_dir


def formatar_erro(mensagem, codigo_erro=None):
    """
    Formata mensagem de erro estruturada
    
    Args:
        mensagem: Mensagem do erro
        codigo_erro: Código do erro (opcional)
    
    Returns:
        dict: Erro estruturado
    """
    return {
        'success': False,
        'message': mensagem,
        'error_code': codigo_erro
    }


def formatar_sucesso(mensagem, dados=None):
    """
    Formata mensagem de sucesso estruturada
    
    Args:
        mensagem: Mensagem de sucesso
        dados: Dados adicionais (opcional)
    
    Returns:
        dict: Sucesso estruturado
    """
    resposta = {
        'success': True,
        'message': mensagem
    }
    if dados:
        resposta['data'] = dados
    return resposta
