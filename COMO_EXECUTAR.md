# 🚀 COMO EXECUTAR A APLICAÇÃO

## ✅ Pré-requisitos

1. **Python 3.8+** instalado
2. **pip** atualizado
3. **Virtual Environment ativado**

---

## 📋 Passos para Executar

### 1️⃣ Ativar Ambiente Virtual

**Windows:**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### 2️⃣ Instalar Dependências

```bash
pip install -r requirements.txt
```

Se faltar algo, instale:
```bash
pip install flask flask-sqlalchemy flask-login werkzeug
```

### 3️⃣ Executar a Aplicação

**Opção 1: Modo Desenvolvimento (Recomendado)**
```bash
python run.py
```
- Porta: **5000**
- Debug: **Ativado**
- Auto-reload: **Ativado**

**Opção 2: Modo Produção**
```bash
python run.py --prod
```
- Porta: **80** (requer privilégios de admin)
- Debug: **Desativado**

**Opção 3: Porta Customizada**
```bash
python run.py --port 8080
```

**Opção 4: Direto (sem script)**
```bash
python app.py
```

---

## 🌐 Acessar a Aplicação

Após executar, abra no navegador:

- **Landing Page:** `http://localhost:5000/`
- **Cardápio Público:** `http://localhost:5000/1` (empresa ID 1)
- **Cadastro:** `http://localhost:5000/cadastro`
- **Login:** `http://localhost:5000/login`

---

## 🧪 Testar Endpoints

### Com curl:

```bash
# Landing page
curl http://localhost:5000/

# Listar cardápio (empresa ID 1)
curl http://localhost:5000/1

# Testar cadastro
curl -X POST http://localhost:5000/cadastro \
  -d "email=teste@example.com&senha=123456&nome_loja=Pizzaria&whatsapp=11999999999"

# Testar login
curl -X POST http://localhost:5000/login \
  -d "email=teste@example.com&senha=123456"
```

### Com Postman:

1. Abra Postman
2. **POST** `http://localhost:5000/cadastro`
   - Body → form-data:
     - email: `teste@example.com`
     - senha: `123456`
     - nome_loja: `Minha Pizzaria`
     - whatsapp: `11999999999`

3. **GET** `http://localhost:5000/1` para ver o cardápio

---

## 🛑 Parar a Aplicação

Pressione **Ctrl + C** no terminal

---

## ❌ Problemas Comuns

### Erro: "ModuleNotFoundError: No module named 'flask'"
```bash
pip install -r requirements.txt
```

### Erro: "Porta 5000 já está em uso"
```bash
python run.py --port 8080
```

### Erro: "database is locked"
```bash
# Remova o banco de dados antigo
rm banco.db
# Rode novamente - ele vai recriar
python run.py
```

### Erro de permissão na porta 80 (Linux)
```bash
# Use porta 5000 ao invés
python run.py --port 5000
```

---

## 📊 Estrutura de Banco de Dados

Na primeira execução, o banco é criado automaticamente em `banco.db` com as tabelas:
- ✅ usuarios
- ✅ empresas
- ✅ produtos
- ✅ imagens

---

## 🔧 Configurações

Para alterar configurações, edite `config.py`:

```python
# Exemplo: Alterar porta do banco de dados
DATABASE_URL = 'sqlite:///meu_banco.db'

# Alterar nível de debug
DEBUG = False
```

---

## 📚 Próximas Verificações

Após executar com sucesso:

1. ✅ Verifique o terminal para mensagens de erro
2. ✅ Teste a página inicial em `http://localhost:5000/`
3. ✅ Tente cadastrar um novo usuário
4. ✅ Tente fazer login
5. ✅ Adicione um produto
6. ✅ Visualize o cardápio

---

## 📚 Documentação

Leia estes arquivos para entender melhor:

- `README_ESTRUTURA.md` - Arquitetura completa
- `GUIA_RAPIDO.md` - Referência rápida
- `EXEMPLOS_USO.py` - Exemplos de código

---

**Tudo pronto para usar! 🎉**
