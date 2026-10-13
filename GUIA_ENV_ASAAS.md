# Variáveis de ambiente e Asaas

As variáveis são carregadas de `.env` pelo `python-dotenv`. Crie o arquivo a
partir de `.env.example` e nunca publique credenciais.

```env
APP_ENV=development
SECRET_KEY=chave-aleatoria-privada
ASAAS_API_KEY=
ASAAS_SANDBOX=True
```

`AsaasService` lê as configurações de `config.py`, sem contexto específico de
framework. O ambiente sandbox usa a API de testes; defina `ASAAS_SANDBOX=False`
somente junto com uma chave de produção.

```python
from app.services.asaas_service import AsaasService

service = AsaasService()
cliente = service.criar_cliente("cliente@example.com", "Nome do Cliente")
```

Para as demais configurações, consulte [CONFIGURACAO_ENV.md](./CONFIGURACAO_ENV.md).
