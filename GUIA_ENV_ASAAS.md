# 🔐 Guia de Variáveis de Ambiente e Integração Asaas

## 📌 Resumo do que foi configurado

✅ **Arquivo `.env`** - Armazena senhas, chaves de API e configurações sensíveis
✅ **Arquivo `.env.example`** - Template para documentar quais variáveis são necessárias
✅ **`python-dotenv`** - Pacote para carregar variáveis do arquivo `.env`
✅ **`AsaasService`** - Serviço pronto para integrar pagamentos
✅ **`config.py`** - Atualizado para usar variáveis de ambiente
✅ **`verificar_config.py`** - Script para validar a configuração

---

## 🚀 Como Usar

### 1️⃣ Primeira vez (Setup inicial)

```bash
# Copiar template de configuração
cp .env.example .env

# Abrir e editar o arquivo .env
nano .env
```

**No `.env`, certifique-se de ter:**
```env
ASAAS_API_KEY=a2739f88-777d-4c85-96b6-b6f18f2e440e
ASAAS_SANDBOX=True
FLASK_ENV=development
```

### 2️⃣ Validar Configuração

```bash
python verificar_config.py
```

Você verá algo como:
```
✅ Arquivo .env
✅ Configuração Asaas
✅ Configuração Flask
✅ Conexão Asaas
✅ Tudo configurado corretamente!
```

### 3️⃣ Usar no Código

```python
from app.services.asaas_service import AsaasService
from flask import current_app

# Usar o serviço em qualquer rota
@app.route('/pagamento', methods=['POST'])
def criar_pagamento():
    service = AsaasService()
    
    # Criar cliente
    cliente = service.criar_cliente(
        email='cliente@example.com',
        nome='João Silva',
        whatsapp='11999999999'
    )
    
    if cliente['success']:
        customer_id = cliente['data']['id']
        
        # Criar cobrança
        pagamento = service.criar_pagamento(
            customer_id=customer_id,
            valor=150.00,
            descricao='Assinatura Plano PRO'
        )
        
        return {'success': True, 'payment_id': pagamento['data']['id']}
```

---

## 🔑 Acessar Variáveis de Ambiente

### No Flask

```python
from flask import current_app

api_key = current_app.config.get('ASAAS_API_KEY')
is_sandbox = current_app.config.get('ASAAS_SANDBOX')
```

### Fora do contexto Flask

```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('ASAAS_API_KEY')
```

---

## 📋 Variáveis Disponíveis

| Variável | Descrição | Obrigatória |
|----------|-----------|------------|
| `ASAAS_API_KEY` | Chave de API do Asaas | ✅ Sim |
| `ASAAS_SANDBOX` | Usar sandbox (True/False) | ✅ Sim |
| `FLASK_ENV` | development ou production | ✅ Sim |
| `SECRET_KEY` | Chave para sessões | ✅ Sim |
| `DATABASE_URL` | URL do banco de dados | ❌ Opcional |
| `MAIL_SERVER` | Servidor SMTP | ❌ Opcional |
| `WEBHOOK_SECRET` | Senha webhook Asaas | ❌ Opcional |

---

## ⚙️ Métodos Disponíveis - AsaasService

### Criar Cliente
```python
service.criar_cliente(
    email='exemplo@email.com',
    nome='João Silva',
    whatsapp='5511999999999'  # opcional
)
```

### Criar Pagamento
```python
service.criar_pagamento(
    customer_id='cus_123456',
    valor=99.90,
    descricao='Pagamento teste',
    due_date='2025-02-28'  # opcional
)
```

### Obter Pagamento
```python
service.obter_pagamento('pay_123456')
```

### Listar Pagamentos
```python
service.listar_pagamentos()  # todos
service.listar_pagamentos(customer_id='cus_123456')  # por cliente
```

### Validar Chave de API
```python
if service.validar_chave_api():
    print("Chave válida!")
```

---

## 🛡️ Segurança - Checklist

- ✅ `.env` está no `.gitignore` (nunca será commitado)
- ✅ Use variáveis de ambiente para TODAS as credenciais
- ✅ NUNCA hardcode senhas ou chaves no código
- ✅ Gere uma nova `SECRET_KEY` para produção
- ✅ Use chaves diferentes para sandbox e produção
- ✅ Configure variáveis no servidor (GitHub Secrets, Vercel, etc.)

---

## 🚀 Próximos Passos

1. **Criar rotas de pagamento** no seu app
2. **Integrar modal de cartão** (Asaas fornece)
3. **Configurar webhooks** para atualizar status de pagamento
4. **Fazer deploy** em produção com variáveis do servidor

---

## 📚 Documentação Oficial

- [Asaas Docs](https://docs.asaas.com/)
- [Sandbox Asaas](https://sandbox.asaas.com/)
- [Python-dotenv](https://github.com/theskumar/python-dotenv)

---

## ❓ Dúvidas Frequentes

**P: Posso compartilhar o arquivo `.env`?**
R: ❌ Nunca! Ele contém suas senhas e chaves de API. Compartilhe apenas o `.env.example`.

**P: Como faço o deploy online?**
R: Defina as variáveis de ambiente no painel do seu servidor (Vercel, Heroku, AWS, etc.).

**P: Minha chave de API é válida?**
R: Execute `python verificar_config.py` para validar.

**P: Como mudo para modo de produção?**
R: Altere no `.env`:
```env
ASAAS_SANDBOX=False
ASAAS_API_KEY=sua-chave-producao
FLASK_ENV=production
```
