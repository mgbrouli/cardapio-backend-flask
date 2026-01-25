#!/usr/bin/env python
"""
Script para testar atualização de empresa via service
"""
from app import create_app, db
from app.models import Empresa
from app.services.empresa_service import EmpresaService

app = create_app()
empresa_service = EmpresaService()

with app.app_context():
    # Buscar primeira empresa
    empresa = Empresa.query.first()
    
    if empresa:
        print(f"Empresa encontrada: {empresa.name_est}")
        print(f"Nome anterior: {empresa.name_est}")
        print(f"CNPJ anterior: {empresa.cnpj_est}")
        
        # Preparar dados de teste
        dados = {
            'nome_est': 'Teste Atualização ' + str(__import__('time').time()),
            'cnpj_est': '99.999.999/9999-99',
            'whatsapp': '5585987654321',
        }
        
        # Atualizar via service
        resultado = empresa_service.atualizar_configuracoes(empresa.id, dados, '/tmp')
        print(f"\nResultado da atualização: {resultado}")
        
        # Buscar novamente do banco
        empresa_reloaded = Empresa.query.get(empresa.id)
        print(f"\nNome depois (banco): {empresa_reloaded.name_est}")
        print(f"CNPJ depois (banco): {empresa_reloaded.cnpj_est}")
        print(f"WhatsApp depois (banco): {empresa_reloaded.whatsapp}")
    else:
        print("Nenhuma empresa encontrada no banco")
