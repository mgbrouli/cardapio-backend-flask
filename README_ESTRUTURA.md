# 📁 Estrutura do Projeto - Cardápio Flask

## 🎯 Padrão Arquitetural: Repository + Service Layer

Este projeto foi reorganizado seguindo as melhores práticas de engenharia de software usando dois padrões de design consolidados:

### **Repository Pattern**
- **Propósito**: Abstrair a camada de acesso aos dados
- **Benefício**: Mudanças no banco de dados não afetam a lógica de negócio
- **Localização**: `/app/repositories/`

### **Service Layer (Camada de Serviços)**
- **Propósito**: Centralizar a lógica de negócio
- **Benefício**: Facilita testes e reutilização de código
- **Localização**: `/app/services/`

---

## 📂 Estrutura de Diretórios

```
cardapio-backend-flask/
│
├── app/
│   ├── models/
│   │   └── __init__.py          # Modelos SQLAlchemy (Empresa, Usuario, Produtos, Imagens)
│   │
│   ├── repositories/
│   │   ├── base_repository.py   # Classe base com operações CRUD genéricas
│   │   ├── produto_repository.py
│   │   ├── imagem_repository.py
│   │   ├── empresa_repository.py
│   │   ├── usuario_repository.py
│   │   └── __init__.py
│   │
│   ├── services/
│   │   ├── produto_service.py   # Lógica de produtos
│   │   ├── empresa_service.py   # Lógica de empresas/configurações
│   │   ├── auth_service.py      # Autenticação e registro
│   │   └── __init__.py
│   │
│   ├── routes/
│   │   ├── public_routes.py     # Rotas públicas (cardápio)
│   │   ├── auth_routes.py       # Autenticação (login, cadastro)
│   │   ├── produto_routes.py    # CRUD de produtos
│   │   ├── empresa_routes.py    # Configurações de empresa
│   │   └── __init__.py
│   │
│   └── utils/
│       └── __init__.py          # Funções utilitárias (pode ser expandido)
│
├── config.py                    # Configurações da aplicação
├── app.py                       # Aplicação principal
├── banco.db                     # Banco de dados SQLite
└── requirements.txt
```

---

## 🔄 Fluxo de Requisições

### Exemplo: Criar um Produto

```
Request HTTP (POST /produto/add/1)
    ↓
app.py (Flask app)
    ↓
produto_routes.py (Blueprint)
    ↓
produto_service.py (ProdutoService)
    ├─→ Valida dados
    ├─→ Chama ProdutoRepository.create()
    └─→ Chama ImagemRepository.create()
    ↓
produto_repository.py (BaseRepository)
    ├─→ Cria modelo Produto
    ├─→ Executa db.session.commit()
    └─→ Retorna resultado
    ↓
Response JSON ou Redirect
```

---

## 💡 Design Patterns Utilizados

### 1. **Repository Pattern**
**Vantagem**: Isolamento da lógica de acesso aos dados

```python
# Antes (sem padrão):
def get_all_prod():
    return Produtos.query.all()

# Depois (Repository Pattern):
class ProdutoRepository(BaseRepository):
    def get_by_empresa(self, empresa_id):
        return Produtos.query.filter_by(empresa_id=empresa_id).all()
```

### 2. **Service Layer**
**Vantagem**: Centralizar regras de negócio e facilitar testes

```python
class ProdutoService:
    def criar_produto(self, empresa_id, nome, ingredientes, preco, 
                     image_name=None, image_data=None):
        # Validar dados
        # Orquestrar repositórios
        # Retornar resultado estruturado
        pass
```

### 3. **Blueprint Pattern (Flask)**
**Vantagem**: Organizar rotas por funcionalidade

```python
# Separação clara de responsabilidades:
public_bp          # Rotas públicas (landing, cardápio)
auth_bp            # Autenticação (login, cadastro)
produto_bp         # Gerencimento de produtos
empresa_bp         # Configurações
```

### 4. **Factory Pattern**
**Vantagem**: Criar a aplicação com configurações

```python
def create_app(config=None):
    app = Flask(__name__)
    # Inicializar extensões
    # Registrar blueprints
    return app
```

---

## 🚀 Como Usar

### Iniciar a aplicação

```bash
python app.py
```

### Acessar endpoints

**Públicos:**
- `GET /` - Landing page
- `GET /<empresa_id>` - Cardápio público

**Autenticação:**
- `POST /cadastro` - Registrar novo usuário
- `POST /login` - Login
- `GET /logout` - Logout

**Produtos (requer autenticação):**
- `POST /produto/add/<empresa_id>` - Adicionar produto
- `POST /produto/edit/<produto_id>` - Editar produto
- `DELETE /produto/delete/<produto_id>` - Deletar produto

**Empresa (requer autenticação):**
- `GET /empresa/home` - Dashboard
- `GET /empresa/config/<empresa_id>` - Configurações
- `POST /empresa/config/<empresa_id>` - Atualizar configurações

---

## 🔧 Adicionar Novas Funcionalidades

### Exemplo: Adicionar novo endpoint

1. **Criar método no Repository** (`app/repositories/novo_repository.py`):
```python
def get_by_filtro(self, filtro):
    return self.model.query.filter_by(**filtro).all()
```

2. **Criar lógica no Service** (`app/services/novo_service.py`):
```python
def obter_dados_filtrados(self, filtro):
    return self.repo.get_by_filtro(filtro)
```

3. **Criar rota no Blueprint** (`app/routes/novo_routes.py`):
```python
@novo_bp.route('/dados', methods=['GET'])
def get_dados():
    resultado = novo_service.obter_dados_filtrados(request.args)
    return jsonify(resultado)
```

4. **Registrar Blueprint** em `app.py`:
```python
app.register_blueprint(novo_bp, url_prefix='/novo')
```

---

## 📊 Vantagens da Nova Estrutura

| Aspecto | Antes | Depois |
|--------|-------|--------|
| **Manutenibilidade** | Difícil - lógica espalhada | Fácil - separação clara |
| **Testabilidade** | Difícil - tudo acoplado | Fácil - componentes isolados |
| **Reutilização** | Baixa - código duplicado | Alta - serviços compartilhados |
| **Escalabilidade** | Limitada | Excelente |
| **Documentação** | Implícita | Explícita |

---

## 🧪 Testando a Aplicação

### Estrutura pronta para testes unitários:

```python
# test_produto_service.py
def test_criar_produto():
    service = ProdutoService()
    resultado = service.criar_produto(
        empresa_id=1,
        nome="Pizza",
        ingredientes="Queijo",
        preco=30.00
    )
    assert resultado['success'] == True
```

---

## 📝 Notas Importantes

- **Backward Compatibility**: Rotas antigas ainda funcionam (redirecionam)
- **Configurações**: Use `config.py` para variáveis de ambiente
- **Banco de Dados**: Migrations podem ser adicionadas com Alembic
- **Validação**: Adicione validação com `wtforms` ou `marshmallow`

---

## 🛠️ Próximas Melhorias Sugeridas

1. ✅ Adicionar testes automatizados
2. ✅ Implementar logging
3. ✅ Adicionar validação de entrada
4. ✅ Implementar cache
5. ✅ Adicionar tratamento de erros centralizado
6. ✅ Implementar API REST com responses estruturadas
7. ✅ Adicionar autenticação por tokens (JWT)

---

**Projeto refatorado em: 25/01/2026**
