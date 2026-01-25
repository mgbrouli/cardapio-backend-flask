"""
Aplicação principal Flask - Cardápio

Para executar:
    python app.py          # Modo desenvolvimento
    python run.py          # Com configurações adicionais
"""

from app import create_app

# Criar aplicação
app = create_app()

if __name__ == '__main__':
    # Desenvolvimento: porta 5000 (sem privilégios)
    # Produção: porta 80 (requer privilégios)
    app.run(host="0.0.0.0", port=5000, debug=True)
