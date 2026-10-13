# Estrutura atual

```text
main.py
app/
  __init__.py
  database.py
  security.py
  templating.py
  models/
  repositories/
  routes/
  services/
  utils/
templates/
static/
config.py
requirements.txt
```

O backend HTTP é FastAPI/ASGI servido por Uvicorn; os modelos SQLAlchemy e o
banco SQLite existente são mantidos. Consulte [ARQUITETURA.md](./ARQUITETURA.md)
para o fluxo e [COMO_EXECUTAR.md](./COMO_EXECUTAR.md) para inicialização.
