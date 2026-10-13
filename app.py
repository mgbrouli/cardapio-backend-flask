"""Entrypoint de compatibilidade para iniciar o servidor FastAPI."""

import uvicorn

from main import app

__all__ = ["app"]


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
