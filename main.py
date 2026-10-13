"""Aplicação ASGI para execução com Uvicorn."""

from app import create_app

app = create_app()
