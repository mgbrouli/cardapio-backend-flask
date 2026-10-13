#!/usr/bin/env python
"""Executa o servidor FastAPI com Uvicorn."""

import argparse

import uvicorn


def main():
    parser = argparse.ArgumentParser(description="Servidor Cardápio FastAPI")
    parser.add_argument("--port", type=int)
    parser.add_argument("--prod", action="store_true")
    args = parser.parse_args()

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=args.port if args.port is not None else (80 if args.prod else 5000),
        reload=not args.prod,
    )


if __name__ == "__main__":
    main()
