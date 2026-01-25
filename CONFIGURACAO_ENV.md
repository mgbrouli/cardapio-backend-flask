# 🔐 Configuração de Variáveis de Ambiente

Este documento explica como configurar as variáveis de ambiente para a aplicação Cardápio Flask.

## 📋 Arquivo `.env`

O arquivo `.env` contém as variáveis sensíveis da aplicação (senhas, chaves de API, etc.). **Nunca commit este arquivo para o repositório Git!**

### Criar arquivo `.env`

1. Na raiz do projeto, copie o arquivo `.env.example`:
   ```bash
   cp .env.example .env
   ```

2. Edite o arquivo `.env` com suas credenciais:
   ```bash
   nano .env
   ```

### Variáveis Obrigatórias

#### Asaas (Pagamentos)
```env
# Chave de API do Asaas para ambiente de testes
ASAAS_API_KEY=a2739f88-777d-4c85-96b6-b6f18f2e440e

# Usar sandbox (true) ou produção (false)
ASAAS_SANDBOX=True
```

#### Flask
```env
# Chave secreta para sessões e tokens
SECRET_KEY=sua-chave-secreta-muito-segura-e-aleatoria

# Ambiente: development ou production
FLASK_ENV=development
```

### Variáveis Opcionais

#### Email
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-de-aplicacao
```

#### Webhook
```env
WEBHOOK_SECRET=sua-senha-webhook-asaas
```

---

## 🚀 Primeiros Passos com Asaas

### 1. Criar Conta Sandbox

1. Acesse: https://sandbox.asaas.com/
2. Registre-se com uma conta de teste
3. Copie a **API Key** gerada

### 2. Adicionar ao `.env`

```env
ASAAS_API_KEY=sua-chave-aqui
ASAAS_SANDBOX=True
```

### 3. Testar Integração

```python
from app.services.asaas_service import AsaasService
from app import create_app

app = create_app()
with app.app_context():
    service = AsaasService()
    if service.validar_chave_api():
        print("✅ Chave de API válida!")
    else:
        print("❌ Chave de API inválida!")
```

---

## 🔄 Migração para Produção

### Ao fazer deploy:

1. **Gere uma nova `SECRET_KEY`:**
   ```python
   import secrets
   print(secrets.token_urlsafe(32))
   ```

2. **Mude para produção no Asaas:**
   - Acesse: https://app.asaas.com/
   - Copie a API Key de produção
   - Atualize `.env`:
     ```env
     ASAAS_API_KEY=sua-chave-producao
     ASAAS_SANDBOX=False
     FLASK_ENV=production
     ```

3. **Configure os Webhooks do Asaas:**
   - Dashboard > Configurações > Webhooks
   - URL: `https://seu-dominio.com/webhooks/asaas`
   - Selecione eventos de pagamento

---

## ⚠️ Segurança

### ✅ Fazer

- ✅ Adicione `.env` ao `.gitignore` (já configurado)
- ✅ Use chaves diferentes para dev e produção
- ✅ Gere `SECRET_KEY` aleatória para produção
- ✅ Nunca compartilhe `.env` por email/chat

### ❌ Não Fazer

- ❌ Commit `.env` para o Git
- ❌ Use a mesma chave em múltiplos ambientes
- ❌ Compartilhe credenciais por canais inseguros
- ❌ Exponha chaves em logs ou mensagens de erro

---

## 📚 Referências

- [Documentação Asaas](https://docs.asaas.com/)
- [Sandbox Asaas](https://sandbox.asaas.com/)
- [Python-dotenv](https://github.com/theskumar/python-dotenv)
