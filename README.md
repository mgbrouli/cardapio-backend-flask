# Cardápio Digital

Aplicação SaaS para empresas criarem e publicarem seus cardápios digitais. O
backend usa FastAPI e Uvicorn; as páginas existentes são renderizadas com Jinja2
e os arquivos estáticos são servidos pelo Starlette.

## Requisitos e execução

Use uma instalação Python compatível com as dependências do projeto. Recomenda-se
criar um ambiente virtual antes de instalar os pacotes:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

O servidor de desenvolvimento fica disponível em `http://localhost:5000` e
recarrega automaticamente quando o código muda. Para escolher outra porta:

```powershell
python run.py --port 8080
```

Também é possível iniciar Uvicorn diretamente:

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

Para produção, configure `APP_ENV=production`, defina uma `SECRET_KEY` aleatória
e privada e inicie com:

```powershell
python run.py --prod
```

O modo de produção desativa o recarregamento e usa a porta 80 por padrão. Use
`--port` para selecionar outra porta. A interface OpenAPI do FastAPI fica em
`/docs`.

## Funcionalidades e endereços

- `/` — página inicial e lista pública de empresas.
- `/{empresa_id}` — cardápio público de uma empresa.
- `/cadastro` e `/login` — cadastro e autenticação.
- `/redefinir-senha` — solicitar redefinição por e-mail.
- `/empresa/home` — painel da empresa autenticada.
- `/admin` — painel da plataforma, restrito aos e-mails definidos em
  `ADMIN_EMAILS`.
- A empresa vinculada a uma conta de `ADMIN_EMAILS` é interna: não aparece na
  vitrine pública e o endereço do seu cardápio exibe a página de suporte.
- `/webhooks/asaas` e `/webhooks/stripe` — notificações autenticadas dos
  provedores de pagamento.

As rotas de produtos permitem criar, editar e excluir itens; as rotas existentes
usadas pelo frontend foram mantidas para compatibilidade.

## Configuração

Copie `.env.example` para `.env` e ajuste os valores conforme o ambiente. Não
publique `.env`, chaves de API ou segredos no controle de versão.

```env
APP_ENV=development
SECRET_KEY=gere-uma-chave-aleatoria-e-privada
DATABASE_URL=sqlite:///caminho/para/banco.db
ASAAS_API_KEY=
ASAAS_SANDBOX=True
WEBHOOK_SECRET=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
PUBLIC_BASE_URL=https://seu-dominio.com
ADMIN_EMAILS=
```

- `APP_ENV`: `development`, `production` ou `testing`.
- `SECRET_KEY`: chave usada para assinar cookies de sessão. Em produção, use
  uma chave aleatória e privada. Para gerar uma:
  `python -c "import secrets; print(secrets.token_urlsafe(32))"`.
- `DATABASE_URL`: endereço do banco. Se não for definido, o projeto usa
  `banco.db` na raiz.
- `ASAAS_API_KEY` e `ASAAS_SANDBOX`: chave da API e seleção do ambiente Asaas.
  Use `ASAAS_SANDBOX=False` somente com credenciais de produção.
- `WEBHOOK_SECRET`: token configurado para autenticar o webhook Asaas.
- `STRIPE_SECRET_KEY` e `STRIPE_WEBHOOK_SECRET`: chave secreta e segredo de
  assinatura do webhook Stripe.
- `PUBLIC_BASE_URL`: endereço público usado para URLs de retorno; em produção,
  deve usar HTTPS.
- `ADMIN_EMAILS`: lista separada por vírgulas dos e-mails de contas já
  cadastradas autorizadas a acessar `/admin`.
- `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD` e `MAIL_FROM`:
  configuração SMTP necessária para enviar links de redefinição de senha e
  confirmação de cadastro. Links de redefinição valem uma hora e são de uso
  único; confirmações valem 24 horas. Novos envios têm intervalo mínimo de um
  minuto. Para Gmail, use uma senha de aplicativo, não a senha normal da conta.
- `REQUIRE_EMAIL_VERIFICATION`: confirmação de e-mail é obrigatória por padrão
  em produção e desativada em desenvolvimento. Defina `True` para testar o
  fluxo localmente; nesse caso, SMTP válido é necessário para novos cadastros.

O painel permite selecionar o provedor ativo entre Asaas e Stripe. A seleção
fica disponível somente quando as credenciais necessárias estão configuradas;
as chaves permanecem no ambiente do servidor e não são exibidas no painel.
Configure os webhooks nos painéis dos provedores para `/webhooks/asaas` e
`/webhooks/stripe`, respectivamente.

Exemplo de uso do serviço Asaas:

```python
from app.services.asaas_service import AsaasService

service = AsaasService()
cliente = service.criar_cliente("cliente@example.com", "Nome do Cliente")
```

## Planos e pagamentos

- O plano grátis permite cadastrar até 10 produtos e alterar os dados gerais e
  o logotipo da empresa.
- Os planos Pro e Premium permitem cadastrar produtos sem limite e alterar as
  cores e o banner.
- A seleção de um plano não ativa uma assinatura. O plano pago é ativado após
  confirmação do pagamento por um webhook autenticado do provedor.
- Falha, atraso, estorno ou cancelamento informado pelo provedor pode retornar
  a empresa ao plano grátis.
- Os preços configurados são R$ 49/mês para Pro e R$ 99/mês para Premium.
- O painel administrativo apresenta usuários com atividade recente por meio de
  heartbeat. O produto não registra pedidos ou vendas e, portanto, não calcula
  faturamento das empresas.

As tabelas de assinatura, eventos de webhook e atividade são criadas pela
aplicação junto ao schema existente. O banco SQLite atual é reutilizado; faça
backup antes de alterações operacionais e use `DATABASE_URL` para configurar
outro banco.

## Arquitetura

- `main.py` e `app/__init__.py`: aplicação ASGI, factory, middleware e registro
  das rotas.
- `app/routes/`: endpoints públicos, autenticação, administração, empresas,
  produtos e webhooks.
- `app/services/`: regras de negócio, autenticação, pagamentos e processamento
  de imagens.
- `app/repositories/`: operações de persistência.
- `app/models/` e `app/database.py`: modelos e sessões SQLAlchemy.
- `app/security.py`: autenticação de sessão, autorização administrativa e
  suporte a CSRF.
- `templates/` e `static/`: interface Jinja2, recursos estáticos e uploads.
- `config.py`: configuração dos ambientes.

O middleware abre um escopo SQLAlchemy por requisição; dependências protegem as
rotas privadas e carregam o usuário atual. Os endpoints chamam os serviços e
repositórios, e retornam templates, redirecionamentos ou respostas HTTP.

## Autenticação e segurança

Senhas novas são armazenadas com Argon2. Hashes legados Werkzeug continuam
verificáveis e são substituídos por hashes Argon2 após um login bem-sucedido.
Senhas legadas armazenadas em texto simples também são comparadas durante o
login e convertidas imediatamente para Argon2 após uma autenticação válida.
Quando habilitada, a confirmação de e-mail é exigida para novos cadastros;
contas existentes continuam válidas. O login bloqueia novas tentativas por 15
minutos após cinco falhas, registradas por e-mail e endereço IP.
Formulários protegidos usam tokens CSRF; as rotas privadas verificam a sessão e
a titularidade dos recursos. Uploads de imagens têm validações de tipo e
tamanho.

## Histórico

- A aplicação foi migrada de Flask para FastAPI, Uvicorn e sessões Starlette,
  mantendo o banco SQLite existente e as páginas atuais.
- O código foi organizado em rotas, serviços, repositórios e modelos.
- Foram adicionados planos, cotas por conta, integrações de checkout e webhook
  para Asaas e Stripe, e um painel administrativo.
