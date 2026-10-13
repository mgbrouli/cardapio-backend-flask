"""Serviço para integração com Asaas - Pagamentos"""
import requests
from typing import Dict, Optional
from config import get_config


class AsaasService:
    """Serviço para comunicação com API do Asaas"""
    
    def __init__(self):
        settings = get_config()
        self.api_key = settings.ASAAS_API_KEY
        self.base_url = settings.ASAAS_BASE_URL
        self.headers = {
            'access_token': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def criar_cliente(self, email: str, nome: str, whatsapp: Optional[str] = None) -> Dict:
        """
        Cria um cliente no Asaas
        
        Args:
            email: Email do cliente
            nome: Nome do cliente
            whatsapp: WhatsApp do cliente (opcional)
        
        Returns:
            Dicionário com resposta da API
        """
        url = f'{self.base_url}/customers'
        
        payload = {
            'name': nome,
            'email': email,
            'mobilePhone': whatsapp
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            return {
                'success': True,
                'data': response.json()
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': f'Erro ao criar cliente no Asaas: {str(e)}'
            }
    
    def criar_pagamento(self, customer_id: str, valor: float, descricao: str, 
                       due_date: Optional[str] = None) -> Dict:
        """
        Cria uma cobrança (payment) no Asaas
        
        Args:
            customer_id: ID do cliente no Asaas
            valor: Valor da cobrança em reais
            descricao: Descrição da cobrança
            due_date: Data de vencimento (formato: YYYY-MM-DD)
        
        Returns:
            Dicionário com resposta da API
        """
        url = f'{self.base_url}/payments'
        
        payload = {
            'customerId': customer_id,
            'value': valor,
            'description': descricao,
            'billingType': 'CREDIT_CARD',  # Para cartão de crédito
        }
        
        if due_date:
            payload['dueDate'] = due_date
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            return {
                'success': True,
                'data': response.json()
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': f'Erro ao criar pagamento no Asaas: {str(e)}'
            }
    
    def obter_pagamento(self, payment_id: str) -> Dict:
        """
        Obtém informações de um pagamento
        
        Args:
            payment_id: ID do pagamento no Asaas
        
        Returns:
            Dicionário com resposta da API
        """
        url = f'{self.base_url}/payments/{payment_id}'
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return {
                'success': True,
                'data': response.json()
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': f'Erro ao obter pagamento no Asaas: {str(e)}'
            }
    
    def listar_pagamentos(self, customer_id: Optional[str] = None) -> Dict:
        """
        Lista pagamentos (opcionalmente filtrados por cliente)
        
        Args:
            customer_id: ID do cliente para filtrar (opcional)
        
        Returns:
            Dicionário com resposta da API
        """
        url = f'{self.base_url}/payments'
        params = {}
        
        if customer_id:
            params['customerId'] = customer_id
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return {
                'success': True,
                'data': response.json()
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': f'Erro ao listar pagamentos no Asaas: {str(e)}'
            }
    
    def validar_chave_api(self) -> bool:
        """
        Valida se a chave de API é válida
        
        Returns:
            True se válida, False caso contrário
        """
        if not self.api_key:
            return False
        
        url = f'{self.base_url}/customers'
        
        try:
            response = requests.get(url, headers=self.headers, timeout=5)
            return response.status_code in [200, 400]  # 200 = válida, 400 = sem dados
        except:
            return False
