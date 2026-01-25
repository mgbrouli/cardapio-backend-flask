# 🏗️ ARQUITETURA - CARDÁPIO FLASK

## 📊 Diagrama de Camadas

```
┌────────────────────────────────────────────────────────────────┐
│                    FRONTEND / CLIENTE                          │
│                 (HTML, JavaScript, CSS)                        │
└────────────────────────────────────────────────────────────────┘
                               ↓
┌────────────────────────────────────────────────────────────────┐
│                       CAMADA DE ROTAS                          │
│                     (Blueprints Flask)                         │
│  ┌─────────────┬────────────┬──────────────┬────────────────┐  │
│  │   public    │    auth    │   produto    │    empresa     │  │
│  │  _routes.py │_routes.py  │ _routes.py   │  _routes.py    │  │
│  └─────────────┴────────────┴──────────────┴────────────────┘  │
└────────────────────────────────────────────────────────────────┘
                               ↓
┌────────────────────────────────────────────────────────────────┐
│                    CAMADA DE SERVIÇOS                          │
│              (Lógica de Negócio / Business Logic)              │
│  ┌──────────────┬──────────────┬──────────────────────────┐   │
│  │ProdutoService│EmpresaService│    AuthService           │   │
│  │              │              │                          │   │
│  │• criar       │• obter       │• registrar_usuario       │   │
│  │• atualizar   │• atualizar   │• validar_credenciais    │   │
│  │• deletar     │• processar   │• obter_usuario           │   │
│  │• listar      │  uploads     │                          │   │
│  └──────────────┴──────────────┴──────────────────────────┘   │
└────────────────────────────────────────────────────────────────┘
                               ↓
┌────────────────────────────────────────────────────────────────┐
│                  CAMADA DE REPOSITÓRIOS                        │
│            (Acesso aos Dados / Data Access Layer)              │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │            BaseRepository (Genérico)                    │  │
│  │  ┌─────────────────────────────────────────────────┐   │  │
│  │  │ create() │ get_by_id() │ update() │ delete()   │   │  │
│  │  └─────────────────────────────────────────────────┘   │  │
│  └─────────────────────────────────────────────────────────┘  │
│  ┌──────────────┬──────────────┬────────────┬───────────────┐ │
│  │ProdutoRepo   │UsuarioRepo   │ImagemRepo  │ EmpresaRepo   │ │
│  │              │              │            │               │ │
│  │Métodos       │ get_by_email │get_by_     │get_ativa_    │ │
│  │específicos   │ email_exists │produto     │by_id         │ │
│  └──────────────┴──────────────┴────────────┴───────────────┘ │
└────────────────────────────────────────────────────────────────┘
                               ↓
┌────────────────────────────────────────────────────────────────┐
│                    CAMADA DE MODELOS                           │
│                  (SQLAlchemy Models)                           │
│  ┌──────────┬──────────┬────────────┬────────────────────┐    │
│  │Produtos  │ Imagens  │  Usuario   │    Empresa         │    │
│  └──────────┴──────────┴────────────┴────────────────────┘    │
└────────────────────────────────────────────────────────────────┘
                               ↓
┌────────────────────────────────────────────────────────────────┐
│                    BANCO DE DADOS                              │
│                  (SQLite - banco.db)                           │
└────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Fluxo de uma Requisição

### Exemplo: POST /produto/add/1 (Adicionar Produto)

```
1. Cliente (HTML/JavaScript)
   ↓ POST /produto/add/1
   
2. Flask Route Handler
   app.py → produto_bp.add_produto()
   ├─ Validar autenticação (@login_required)
   ├─ Verificar permissões (empresa_id)
   └─ Processar arquivo (imagem)
   
3. Camada de Serviços
   produto_service.criar_produto()
   ├─ Validar dados (preço)
   ├─ Chamar ProdutoRepository.create()
   └─ Chamar ImagemRepository.create()
   
4. Camada de Repositórios
   produto_repo.create(dados)
   ├─ Criar instância de Produto
   ├─ db.session.add()
   ├─ db.session.commit()
   └─ Retornar objeto
   
5. Banco de Dados
   Salvar em: produtos table
   
6. Response
   ← Redirect /empresa/home
```

---

## 🎯 Separação de Responsabilidades

### Cada Camada Faz Uma Coisa Bem

| Camada | Responsabilidade | Exemplo |
|--------|------------------|---------|
| **Routes** | Receber requisições, validar entrada, chamar serviços | Validar empresa_id do user |
| **Services** | Lógica de negócio, orquestração | Decidir quando criar imagem |
| **Repositories** | CRUD puro, acesso aos dados | Executar query SQL |
| **Models** | Estrutura dos dados | Definir campos da tabela |
| **Database** | Persistência | Armazenar dados |

---

## 💾 Exemplo: Estrutura de Dados

### Requisição Criar Produto

```python
# Input (Request)
{
    "nome": "Pizza Margherita",
    "ingredientes": "Tomate, Queijo",
    "preco": "35.00",
    "image": <arquivo.jpg>
}

# Services retorna
{
    'success': True,
    'message': 'Produto adicionado com sucesso',
    'produto_id': 1
}

# Banco de Dados
Produtos Table:
├─ id: 1
├─ nome: "Pizza Margherita"
├─ ingredientes: "Tomate, Queijo"
├─ preco: 35.0
└─ empresa_id: 1

Imagens Table:
├─ id: 1
├─ name: "arquivo.jpg"
├─ image: <binary data>
├─ produto_id: 1
└─ empresa_id: 1
```

---

## 🔐 Fluxo de Autenticação

```
Cliente
  ↓ POST /login
  ├─ email: "user@example.com"
  └─ senha: "123456"
  ↓
auth_routes.login()
  ├─ auth_service.validar_credenciais()
  │  ├─ usuario_repo.get_by_email()
  │  └─ check_password_hash()
  └─ login_user() ← Flask-Login
  ↓
Redirect /empresa/home
  ↓
@login_required ← Protected Routes
```

---

## 📦 Dependências de Código

```
app.py (Principal)
├── config.py (Configurações)
├── app/models/__init__.py (SQLAlchemy)
│
├── app/routes/
│   ├── public_routes.py
│   ├── auth_routes.py
│   ├── produto_routes.py
│   └── empresa_routes.py
│       ↓ Importam
│
├── app/services/
│   ├── produto_service.py
│   ├── empresa_service.py
│   └── auth_service.py
│       ↓ Importam
│
└── app/repositories/
    ├── base_repository.py
    ├── produto_repository.py
    ├── empresa_repository.py
    └── usuario_repository.py
        ↓ Usam
    app/models/
```

---

## 🚀 Adicionar Novo Recurso

### Passo 1: Criar Modelo
```python
# app/models/__init__.py
class NovoModelo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
```

### Passo 2: Criar Repository
```python
# app/repositories/novo_repository.py
class NovoRepository(BaseRepository):
    def __init__(self):
        super().__init__(NovoModelo)
```

### Passo 3: Criar Service
```python
# app/services/novo_service.py
class NovoService:
    def __init__(self):
        self.repo = NovoRepository()
    
    def criar(self, dados):
        return self.repo.create(**dados)
```

### Passo 4: Criar Routes
```python
# app/routes/novo_routes.py
@novo_bp.route('/criar', methods=['POST'])
@login_required
def criar():
    service = NovoService()
    resultado = service.criar(request.json)
    return redirect(...)
```

### Passo 5: Registrar Blueprint
```python
# app.py
app.register_blueprint(novo_bp, url_prefix='/novo')
```

---

## 🧪 Testabilidade

A nova estrutura permite testes isolados:

```python
# Test Services (sem acesso a BD)
def test_criar_produto():
    service = ProdutoService()
    resultado = service.criar_produto(...)
    assert resultado['success'] == True

# Test Repositories (com BD de teste)
def test_produto_repository():
    repo = ProdutoRepository()
    produto = repo.create(...)
    assert produto.id is not None

# Test Routes (com cliente de teste Flask)
def test_add_produto_route():
    response = client.post('/produto/add/1', data={...})
    assert response.status_code == 302
```

---

## 📋 Checklist de Boas Práticas

- ✅ Separação de responsabilidades
- ✅ DRY (Don't Repeat Yourself)
- ✅ SOLID principles
- ✅ Fácil de testar
- ✅ Fácil de manter
- ✅ Fácil de escalar
- ✅ Fácil de debugar
- ✅ Documentação clara

---

**Última atualização: 25/01/2026**
