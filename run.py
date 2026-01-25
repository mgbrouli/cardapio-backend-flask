#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para executar a aplicação Flask - Cardápio

Uso:
    python run.py              # Desenvolvimento (porta 5000)
    python run.py --prod       # Produção (porta 80)
    python run.py --port 8080  # Porta customizada
"""

import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app


def main():
    """Função principal para rodar a aplicação"""
    
    # Parsear argumentos
    port = 5000
    debug = True
    
    if '--prod' in sys.argv:
        port = 80
        debug = False
        print("🔒 Modo Produção - Porta 80")
    
    if '--port' in sys.argv:
        try:
            idx = sys.argv.index('--port')
            port = int(sys.argv[idx + 1])
            print(f"🔧 Porta customizada: {port}")
        except (IndexError, ValueError):
            print("❌ Erro: use --port NUMERO")
            sys.exit(1)
    
    if debug:
        print("🚀 Modo Desenvolvimento - Porta 5000")
        print("⚠️  Use --prod para produção")
    
    # Criar e rodar aplicação
    app = create_app()
    
    print(f"\n{'='*60}")
    print(f"🍕 Cardápio Flask iniciando...")
    print(f"{'='*60}")
    print(f"📱 Acesse: http://localhost:{port}")
    print(f"🛑 Pressione Ctrl+C para parar")
    print(f"{'='*60}\n")
    
    try:
        app.run(host="0.0.0.0", port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n\n🛑 Aplicação interrompida pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro ao iniciar: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
