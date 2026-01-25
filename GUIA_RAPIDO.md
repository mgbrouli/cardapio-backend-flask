# 📚 GUIA RÁPIDO - Cardápio Flask

## 🚀 Iniciar Aplicação

```bash
# Ativar ambiente virtual
source .venv/Scripts/activate  # Windows
source .venv/bin/activate      # Linux/Mac

# Instalar dependências
pip install -r requirements.txt

# Rodar aplicação
python app.py
```

---

## 🗂️ Estrutura Principal

| Arquivo/Pasta | Propósito |
|---|---|
| `app/` | Código da aplicação |
| `app/models/` | Modelos SQLAlchemy |
| `app/repositories/` | Acesso a dados |
| `app/services/` | Lógica de negócio |
| `app/routes/` | Rotas/Endpoints |
| `config.py` | Configurações |
| `app.py` | Aplicação principal |

---

## 🌐 Endpoints Principais

### Públicos
| Método | URL | Descrição |
|--------|-----|-----------|
| GET | `/` | Landing page |
| GET | `/<empresa_id>` | Visualizar cardápio |

### Autenticação
| Método | URL | Descrição |
|--------|-----|-----------|
| GET/POST | `/cadastro` | Registrar novo usuário |
| GET/POST | `/login` | Fazer login |
| GET | `/logout` | Fazer logout |

### Produtos (Autenticado)
| Método | URL | Descrição |
|--------|-----|-----------|
| POST | `/produto/add/<empresa_id>` | Adicionar produto |
| POST | `/produto/edit/<produto_id>` | Editar produto |
| DELETE | `/produto/delete/<produto_id>` | Deletar produto |

### Empresa (Autenticado)
| Método | URL | Descrição |
|--------|-----|-----------|
| GET | `/empresa/home` | Dashboard |
| GET/POST | `/empresa/config/<empresa_id>` | Configurações |

---

## 💻 Como Usar os Services

### Exemplo 1: Criar Produto
```python
from app.services.produto_service import ProdutoService

service = ProdutoService()
resultado = service.criar_produto(
    empresa_id=1,
    nome="Pizza Margherita",
    ingredientes="Tomate, Queijo, Manjericão",
    preco=35.00,
    image_name="pizza.jpg",
    image_data=imagem_bytes
)

if resultado['success']:
    produto_id = resultado['produto_id']
else:
    print(f"Erro: {resultado['message']}")
```

### Exemplo 2: Listar Produtos com Imagens
```python
from app.services.produto_service import ProdutoService

service = ProdutoService()
produtos = service.obter_produtos_com_imagens(empresa_id=1)

for item in produtos:
    produto = item['produto']
    imagem_base64 = item['imagem']
    print(f"{produto.nome} - R$ {produto.preco}")
```

### Exemplo 3: Autenticar Usuário
```python
from app.services.auth_service import AuthService

service = AuthService()
resultado = service.validar_credenciais(
    email="user@example.com",
    senha="senha123"
)

if resultado['success']:
    usuario = resultado['usuario']
    # login_user(usuario) em Flask-Login
else:
    print(f"Erro: {resultado['message']}")
```

### Exemplo 4: Atualizar Configurações de Empresa
```python
from app.services.empresa_service import EmpresaService

service = EmpresaService()
dados = {
    'nome_est': 'Pizzaria Premium',
    'whatsapp': '11999999999',
    'primary_color': '#FF0000',
    'bg_color': '#FFFFFF'
}

resultado = service.atualizar_configuracoes(empresa_id=1, dados=dados, basedir=basedir)
```

---

## 🔧 Estrutura de Resposta dos Services

Todos os services retornam um dict estruturado:

### Sucesso ✅
```python
{
    'success': True,
    'message': 'Operação realizada com sucesso',
    'produto_id': 1,  # Dados adicionais variam
    'usuario_id': 5,
    # etc...
}
```

### Erro ❌
```python
{
    'success': False,
    'message': 'Descrição do erro'
}
```

---

## 📝 Como Adicionar Novo Endpoint

### 1. Criar Service (se necessário)
```python
# app/services/novo_service.py
class NovoService:
    def __init__(self):
        self.repo = NovoRepository()
    
    def fazer_algo(self, dados):
        return self.repo.create(**dados)
```

### 2. Criar Blueprint
```python
# app/routes/novo_routes.py
from flask import Blueprint
novo_bp = Blueprint('novo', __name__, url_prefix='/novo')

@novo_bp.route('/fazer', methods=['POST'])
def fazer():
    service = NovoService()
    resultado = service.fazer_algo(request.json)
    return jsonify(resultado)
```

### 3. Registrar em app.py
```python
from app.routes.novo_routes import novo_bp
app.register_blueprint(novo_bp)
```

---

## 🧪 Testar Manualmente

### Com curl
```bash
# Landing page
curl http://localhost/

# Listar cardápio
curl http://localhost/1

# Registrar
curl -X POST http://localhost/cadastro \
  -d "email=novo@test.com&senha=123&nome_loja=Pizzaria&whatsapp=11999"

# Login
curl -X POST http://localhost/login \
  -d "email=novo@test.com&senha=123"
```

### Com Python
```python
from app import create_app
from app.services.produto_service import ProdutoService

app = create_app()

with app.app_context():
    service = ProdutoService()
    resultado = service.criar_produto(
        empresa_id=1,
        nome="Pizza",
        ingredientes="Queijo",
        preco=30.00
    )
    print(resultado)
```

---

## 🐛 Debugging

### Ver logs
```python
# app/services/produto_service.py
import logging
logger = logging.getLogger(__name__)

logger.debug(f"Criando produto: {nome}")
logger.error(f"Erro: {str(e)}")
```

### Usar debugger
```python
# No ponto problemático
import pdb; pdb.set_trace()
```

### Ver estado do banco
```python
from app.models import Produtos

with app.app_context():
    produtos = Produtos.query.all()
    for p in produtos:
        print(f"{p.nome} - R$ {p.preco}")
```

---

## 📊 Arquivos Importantes

| Arquivo | Alteração | Motivo |
|---------|-----------|--------|
| `config.py` | ✅ Novo | Configurações centralizadas |
| `app.py` | ✅ Refatorado | Factory pattern |
| `model.py` | → `app/models/__init__.py` | Organização |
| `controller.py` | → Dividido em Services | Melhor separação |
| Novos | ✅ Repositories | CRUD abstrato |
| Novos | ✅ Blueprints | Rotas organizadas |

---

## 🔄 Fluxo de Desenvolvimento

```
1. Receber Requisição
   ↓
2. Route (Validar entrada)
   ↓
3. Service (Lógica de negócio)
   ↓
4. Repository (Acesso a dados)
   ↓
5. Database (Persistência)
   ↓
6. Response (Retornar ao cliente)
```

---

## ✅ Checklist de Qualidade

- [ ] Código segue o padrão Repository + Service
- [ ] Services retornam estrutura padrão
- [ ] Não há queries SQL nas rotas
- [ ] Erros são tratados em try/catch
- [ ] Validação de entrada nas rotas
- [ ] Autenticação verificada com @login_required
- [ ] Autorização verificada (usuário é dono?)
- [ ] Testes unitários escritos

---

## 🚨 Troubleshooting

### "ImportError: No module named 'app'"
```bash
# Certifique-se que está rodando de dentro do diretório correto
cd cardapio-backend-flask
python app.py
```

### "sqlalchemy.exc.OperationalError: no such table"
```bash
# Banco de dados não foi criado, remova e deixe recriar
rm banco.db
python -c "from app import create_app; app = create_app(); app.app_context().push()"
```

### "401 Unauthorized" em rota protegida
```bash
# Faça login primeiro
# Ou adicione @login_required na rota
```

---

## 📞 Referências Rápidas

| Conceito | Onde Usar |
|----------|-----------|
| **Validar entrada** | Em `routes/` |
| **Lógica de negócio** | Em `services/` |
| **Queries ao BD** | Em `repositories/` |
| **Relacionamentos** | Em `models/` |
| **Configurações** | Em `config.py` |
| **Login** | Com `@login_required` |
| **Autorização** | Com `current_user` |

---

## 🎓 Conceitos-Chave

- **Repository**: Abstração para acesso a dados
- **Service**: Contém lógica de negócio
- **Blueprint**: Grupo de rotas
- **Factory**: Cria instâncias de forma centralizada
- **ORM**: SQLAlchemy mapeia Python ↔ SQL
- **Validação**: Garantir dados corretos
- **Autenticação**: Quem é você?
- **Autorização**: Você tem permissão?

---

**Última atualização: 25/01/2026**
**Documentação mantida em:** README_ESTRUTURA.md, ARQUITETURA.md, TESTES.md
