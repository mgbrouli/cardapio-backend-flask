# Executar a aplicação

## Requisitos

- Python 3.8 ou superior
- Ambiente virtual recomendado

## Instalação

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Desenvolvimento

```powershell
python run.py
```

O servidor Uvicorn inicia em `http://localhost:5000` e recarrega ao detectar
alterações. Para escolher outra porta, use `python run.py --port 8080`.

Também é possível iniciar diretamente com:

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

Em produção, configure `APP_ENV=production` e uma `SECRET_KEY` aleatória e
privada, depois inicie com `python run.py --prod`. O modo de produção desativa
o recarregamento e usa a porta 80 por padrão; use `--port` para especificar
outra porta.

## URLs principais

- `/` — página inicial
- `/<empresa_id>` — cardápio público
- `/cadastro` e `/login` — cadastro e autenticação
- `/empresa/home` — painel
- `/docs` — documentação OpenAPI interativa do FastAPI

O banco SQLite `banco.db` existente é reutilizado. Hashes de senha Werkzeug
legados continuam válidos; no primeiro login correto são substituídos por
hashes Argon2.
