# Configuração de ambiente

Crie `.env` copiando `.env.example` e defina os valores do seu ambiente.
O arquivo `.env` não deve ser enviado ao controle de versão.

```env
APP_ENV=development
SECRET_KEY=gere-uma-chave-aleatoria-e-privada
DATABASE_URL=sqlite:///caminho/para/banco.db
ASAAS_API_KEY=
ASAAS_SANDBOX=True
WEBHOOK_SECRET=
```

- `APP_ENV`: `development`, `production` ou `testing`.
- `SECRET_KEY`: chave que assina cookies de sessão; obrigatória e aleatória em
  produção. Gere uma com `python -c "import secrets; print(secrets.token_urlsafe(32))"`.
- `DATABASE_URL`: opcional; por padrão o projeto usa `banco.db` na raiz e
  preserva os dados existentes.
- `ASAAS_API_KEY` e `ASAAS_SANDBOX`: credenciais da integração de pagamentos.
- `WEBHOOK_SECRET`: segredo opcional para webhooks.

Para executar em produção, configure `APP_ENV=production` e execute
`python run.py --prod`. Veja [COMO_EXECUTAR.md](./COMO_EXECUTAR.md).
