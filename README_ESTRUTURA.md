# Estrutura do projeto

O backend usa FastAPI, SQLAlchemy e Argon2; as páginas existentes são servidas
por Jinja2 e os arquivos estáticos por Starlette.

```text
main.py                     # Aplicação ASGI (Uvicorn)
app/
  __init__.py               # Factory FastAPI e middleware
  database.py               # Engine e escopo das sessões SQLAlchemy
  security.py               # Dependência de autenticação
  models/                   # Empresa, usuário, produtos e imagens
  repositories/             # Consultas e operações CRUD
  routes/                   # Rotas FastAPI
  services/                 # Regras de negócio e serviços
templates/                  # Interface Jinja2 mantida
static/                     # CSS, imagens e uploads
config.py                   # Configurações por ambiente
requirements.txt            # Dependências
```

Para executar localmente, consulte [COMO_EXECUTAR.md](./COMO_EXECUTAR.md).
O OpenAPI interativo está em `/docs`.
