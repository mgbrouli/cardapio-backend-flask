# 🧪 TESTES - Cardápio Flask

## Estrutura de Testes Recomendada

```
tests/
├── __init__.py
├── conftest.py              # Configuração pytest
├── test_repositories.py
├── test_services.py
├── test_routes.py
└── test_models.py
```

---

## 1️⃣ Setup de Testes (conftest.py)

```python
import pytest
from app import create_app
from app.models import db
from config import TestingConfig


@pytest.fixture
def app():
    """Cria aplicação para testes"""
    app = create_app(TestingConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Cliente de teste Flask"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI runner para testes"""
    return app.test_cli_runner()
```

---

## 2️⃣ Testando Repositories

```python
# tests/test_repositories.py

from app.repositories.produto_repository import ProdutoRepository
from app.models import db, Produtos


def test_create_produto(app):
    """Testa criação de produto"""
    with app.app_context():
        repo = ProdutoRepository()
        
        produto = repo.create(
            empresa_id=1,
            nome="Pizza",
            ingredientes="Queijo",
            preco=30.0
        )
        
        assert produto.id is not None
        assert produto.nome == "Pizza"
        assert produto.preco == 30.0


def test_get_by_empresa(app):
    """Testa busca de produtos por empresa"""
    with app.app_context():
        repo = ProdutoRepository()
        
        # Criar produtos
        repo.create(empresa_id=1, nome="P1", ingredientes="I1", preco=10.0)
        repo.create(empresa_id=1, nome="P2", ingredientes="I2", preco=20.0)
        repo.create(empresa_id=2, nome="P3", ingredientes="I3", preco=30.0)
        
        # Buscar
        produtos = repo.get_by_empresa(1)
        
        assert len(produtos) == 2
        assert all(p.empresa_id == 1 for p in produtos)


def test_update_produto(app):
    """Testa atualização de produto"""
    with app.app_context():
        repo = ProdutoRepository()
        
        # Criar
        produto = repo.create(
            empresa_id=1,
            nome="Pizza",
            ingredientes="Queijo",
            preco=30.0
        )
        
        # Atualizar
        repo.update(produto, nome="Pizza Premium", preco=45.0)
        
        # Verificar
        assert produto.nome == "Pizza Premium"
        assert produto.preco == 45.0


def test_delete_produto(app):
    """Testa exclusão de produto"""
    with app.app_context():
        repo = ProdutoRepository()
        
        # Criar
        produto = repo.create(
            empresa_id=1,
            nome="Pizza",
            ingredientes="Queijo",
            preco=30.0
        )
        produto_id = produto.id
        
        # Deletar
        sucesso = repo.delete_by_id(produto_id)
        
        assert sucesso == True
        assert Produtos.query.get(produto_id) is None
```

---

## 3️⃣ Testando Services

```python
# tests/test_services.py

from app.services.produto_service import ProdutoService
from app.services.auth_service import AuthService


def test_criar_produto_service(app):
    """Testa criação via serviço"""
    with app.app_context():
        service = ProdutoService()
        
        resultado = service.criar_produto(
            empresa_id=1,
            nome="Pizza",
            ingredientes="Queijo",
            preco=30.0
        )
        
        assert resultado['success'] == True
        assert 'produto_id' in resultado


def test_criar_produto_preco_invalido(app):
    """Testa validação de preço"""
    with app.app_context():
        service = ProdutoService()
        
        resultado = service.criar_produto(
            empresa_id=1,
            nome="Pizza",
            ingredientes="Queijo",
            preco="abc"  # Inválido
        )
        
        assert resultado['success'] == False
        assert "Preço" in resultado['message']


def test_registrar_usuario_service(app):
    """Testa registro de usuário"""
    with app.app_context():
        service = AuthService()
        
        resultado = service.registrar_usuario(
            email="user@example.com",
            senha="senha123",
            nome_loja="Minha Pizzaria",
            whatsapp="11999999999"
        )
        
        assert resultado['success'] == True
        assert 'usuario_id' in resultado
        assert 'empresa_id' in resultado


def test_email_duplicado(app):
    """Testa impedimento de email duplicado"""
    with app.app_context():
        service = AuthService()
        
        # Primeiro registro
        service.registrar_usuario(
            email="user@example.com",
            senha="senha123",
            nome_loja="Pizzaria 1",
            whatsapp="11999999999"
        )
        
        # Segundo registro com mesmo email
        resultado = service.registrar_usuario(
            email="user@example.com",
            senha="outra123",
            nome_loja="Pizzaria 2",
            whatsapp="11988888888"
        )
        
        assert resultado['success'] == False
        assert "já está cadastrado" in resultado['message']


def test_validar_credenciais_corretas(app):
    """Testa autenticação com credenciais corretas"""
    with app.app_context():
        service = AuthService()
        
        # Registrar
        service.registrar_usuario(
            email="user@example.com",
            senha="senha123",
            nome_loja="Pizzaria",
            whatsapp="11999999999"
        )
        
        # Validar
        resultado = service.validar_credenciais(
            email="user@example.com",
            senha="senha123"
        )
        
        assert resultado['success'] == True
        assert resultado['usuario'] is not None


def test_validar_credenciais_incorretas(app):
    """Testa autenticação com credenciais incorretas"""
    with app.app_context():
        service = AuthService()
        
        # Registrar
        service.registrar_usuario(
            email="user@example.com",
            senha="senha123",
            nome_loja="Pizzaria",
            whatsapp="11999999999"
        )
        
        # Tentar com senha errada
        resultado = service.validar_credenciais(
            email="user@example.com",
            senha="senhaerrada"
        )
        
        assert resultado['success'] == False
```

---

## 4️⃣ Testando Routes

```python
# tests/test_routes.py

from flask_login import login_user
from app.models import Usuario, Empresa, Produtos


def test_landing_page(client):
    """Testa página de landing"""
    response = client.get('/')
    assert response.status_code == 200


def test_login_page(client):
    """Testa página de login"""
    response = client.get('/login', follow_redirects=True)
    assert response.status_code == 200


def test_cadastro_post(client, app):
    """Testa registro via POST"""
    response = client.post('/cadastro', data={
        'email': 'novo@example.com',
        'senha': 'senha123',
        'nome_loja': 'Pizzaria Nova',
        'whatsapp': '11999999999'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Verificar que foi criado no BD
    with app.app_context():
        usuario = Usuario.query.filter_by(email='novo@example.com').first()
        assert usuario is not None


def test_login_post(client, app):
    """Testa login via POST"""
    # Primeiro criar um usuário
    with app.app_context():
        empresa = Empresa(name_est="Pizzaria", whatsapp="11999999999")
        app.db.session.add(empresa)
        app.db.session.flush()
        
        from werkzeug.security import generate_password_hash
        usuario = Usuario(
            email="user@example.com",
            senha=generate_password_hash("senha123"),
            empresa_id=empresa.id
        )
        app.db.session.add(usuario)
        app.db.session.commit()
    
    # Fazer login
    response = client.post('/login', data={
        'email': 'user@example.com',
        'senha': 'senha123'
    }, follow_redirects=True)
    
    # Verificar redirecionamento
    assert response.status_code == 200
    # Aqui seria verificado se está na página protegida


def test_add_produto_requer_autenticacao(client):
    """Testa se add_produto requer autenticação"""
    response = client.post('/produto/add/1', data={
        'nome': 'Pizza',
        'ingredientes': 'Queijo',
        'preco': '30.00'
    })
    
    # Deve redirecionar para login
    assert response.status_code in [302, 401]


def test_home_requer_autenticacao(client):
    """Testa se home requer autenticação"""
    response = client.get('/empresa/home')
    
    assert response.status_code in [302, 401]
```

---

## 5️⃣ Executar Testes

### Instalação
```bash
pip install pytest pytest-cov
```

### Rodar todos os testes
```bash
pytest
```

### Rodar com cobertura
```bash
pytest --cov=app tests/
```

### Rodar teste específico
```bash
pytest tests/test_services.py::test_criar_produto_service
```

### Modo verbose
```bash
pytest -v
```

---

## 📊 Cobertura de Testes

### Meta
- ✅ Services: 90%+ de cobertura
- ✅ Repositories: 85%+ de cobertura
- ✅ Routes: 80%+ de cobertura
- ✅ Models: 70%+ de cobertura

### Gerar Relatório
```bash
pytest --cov=app --cov-report=html
# Abre: htmlcov/index.html
```

---

## 🔍 Debugging de Testes

### Ver variáveis durante teste
```python
def test_exemplo(app):
    with app.app_context():
        service = ProdutoService()
        resultado = service.criar_produto(...)
        
        # Breakpoint para debugar
        import pdb; pdb.set_trace()
        print(resultado)
```

### Usar pytest fixtures para setup comum
```python
@pytest.fixture
def empresa_com_usuarios(app):
    """Cria dados de teste padrão"""
    with app.app_context():
        empresa = Empresa(name_est="Test", whatsapp="11999")
        db.session.add(empresa)
        db.session.flush()
        
        usuario = Usuario(
            email="test@test.com",
            senha=generate_password_hash("teste"),
            empresa_id=empresa.id
        )
        db.session.add(usuario)
        db.session.commit()
        
        yield {'empresa': empresa, 'usuario': usuario}
```

---

## ✅ Checklist de Testes

- [ ] Testes para cada método de Repository
- [ ] Testes para cada método de Service
- [ ] Testes para cada rota autenticada
- [ ] Testes de validação de entrada
- [ ] Testes de casos de erro
- [ ] Testes de autenticação/autorização
- [ ] Testes de integração
- [ ] Coverage mínimo de 80%

---

**Última atualização: 25/01/2026**
