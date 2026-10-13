# Arquitetura do Cardápio Digital

O backend é uma aplicação ASGI baseada em FastAPI. A interface existente
(templates Jinja2, formulários HTML e recursos estáticos) continua funcionando
sem alteração visual.

## Camadas

- `main.py` e `app/__init__.py`: criação da aplicação, middleware e montagem
  das rotas.
- `app/routes/`: endpoints FastAPI agrupados por domínio.
- `app/services/`: regras de negócio e autenticação.
- `app/repositories/`: acesso a dados.
- `app/models/` e `app/database.py`: modelos e sessões SQLAlchemy.
- `templates/` e `static/`: interface HTML, CSS, JavaScript e uploads.

## Fluxo HTTP

1. Uvicorn recebe a requisição ASGI e FastAPI seleciona a rota.
2. Middleware abre um escopo SQLAlchemy por requisição; `SessionMiddleware`
   fornece o cookie de sessão assinado.
3. As dependências protegem as rotas privadas e carregam o usuário atual.
4. O endpoint chama os serviços e repositórios.
5. FastAPI devolve um template Jinja2, redirecionamento, arquivo estático ou
   resposta HTTP.

## Banco e autenticação

O projeto usa SQLAlchemy 2 com as tabelas existentes, sem recriar ou substituir
o banco SQLite `banco.db`. Para produção, defina `DATABASE_URL` e uma
`SECRET_KEY` forte.

Senhas novas são armazenadas com Argon2. Para manter contas já existentes,
hashes Werkzeug são verificados durante o login e migrados para Argon2 após
uma autenticação bem-sucedida.

## Endpoints mantidos

- `GET /` e `GET /{empresa_id}` — landing page e cardápio público.
- `GET/POST /cadastro` e `GET/POST /login`; `GET /logout`.
- `GET /empresa/home`, configurações e planos.
- Rotas de produto antigas (`/add`, `/edit`, `/remove`) e agrupadas
  (`/produto/add`, `/produto/edit`, `/produto/delete`).

O schema OpenAPI e a interface interativa ficam disponíveis em `/docs`.
