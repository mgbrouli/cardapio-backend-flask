"""
EXEMPLOS DE USO DA NOVA ESTRUTURA
=================================

Este arquivo mostra como usar os serviços e repositórios
da aplicação em diferentes cenários.
"""

# ============================================================================
# 1. USANDO PRODUTO SERVICE
# ============================================================================

from app.services.produto_service import ProdutoService

produto_service = ProdutoService()

# Criar um novo produto
resultado = produto_service.criar_produto(
    empresa_id=1,
    nome="Refrigerante",
    ingredientes="",
    preco=35.00,
    image_name="refrigerante.jpg",
    image_data=b"<dados da imagem>"
)

print(resultado)
# Output: {'success': True, 'message': 'Produto adicionado com sucesso', 'produto_id': 1}


# Obter produtos com imagens de uma empresa
produtos = produto_service.obter_produtos_com_imagens(empresa_id=1)

for item in produtos:
    print(f"Produto: {item['produto'].nome}")
    print(f"Preço: R$ {item['produto'].preco}")
    print(f"Imagem (base64): {item['imagem'][:50]}...")


# Atualizar um produto
resultado = produto_service.atualizar_produto(
    produto_id=1,
    nome="Refrigerante Premium",
    ingredientes="",
    preco=45.00
)

print(resultado)


# Deletar um produto
resultado = produto_service.deletar_produto(produto_id=1)
print(resultado)


# ============================================================================
# 2. USANDO EMPRESA SERVICE
# ============================================================================

from app.services.empresa_service import EmpresaService
import os

empresa_service = EmpresaService()
basedir = os.path.abspath(os.path.dirname(__file__))

# Obter empresa
empresa = empresa_service.obter_empresa(empresa_id=1)
print(f"Empresa: {empresa.name_est}")

# Obter empresa ativa
empresa_ativa = empresa_service.obter_empresa_ativa(empresa_id=1)
if empresa_ativa:
    print("Empresa está ativa!")
else:
    print("Empresa inativa!")


# Atualizar configurações
dados = {
    'nome_est': 'Restaurante Nova',
    'whatsapp': '11999999999',
    'primary_color': '#FF0000',
    'bg_color': '#FFFFFF'
}

resultado = empresa_service.atualizar_configuracoes(empresa_id=1, dados=dados, basedir=basedir)
print(resultado)


# ============================================================================
# 3. USANDO AUTH SERVICE
# ============================================================================

from app.services.auth_service import AuthService

auth_service = AuthService()

# Registrar novo usuário
resultado = auth_service.registrar_usuario(
    email="joao@example.com",
    senha="senha123",
    nome_loja="Restaurante do João",
    whatsapp="11988888888"
)

if resultado['success']:
    print(f"Usuário criado! ID: {resultado['usuario_id']}")
else:
    print(f"Erro: {resultado['message']}")


# Validar credenciais
resultado = auth_service.validar_credenciais(
    email="joao@example.com",
    senha="senha123"
)

if resultado['success']:
    usuario = resultado['usuario']
    print(f"Login bem-sucedido! Usuário: {usuario.email}")
else:
    print(f"Erro: {resultado['message']}")


# ============================================================================
# 4. USANDO REPOSITORIES DIRETAMENTE
# ============================================================================

from app.repositories.produto_repository import ProdutoRepository
from app.repositories.usuario_repository import UsuarioRepository

# Produto Repository
produto_repo = ProdutoRepository()

# Criar produto diretamente
produto = produto_repo.create(
    empresa_id=1,
    nome="Refrigerante",
    ingredientes="Água, Açúcar, Gás",
    preco=5.00
)
print(f"Produto criado: {produto.id}")

# Buscar por empresa
produtos = produto_repo.get_by_empresa(empresa_id=1)
print(f"Total de produtos: {len(produtos)}")

# Atualizar
produto_repo.update(produto, nome="Refrigerante 2L")

# Deletar
produto_repo.delete(produto)


# Usuario Repository
usuario_repo = UsuarioRepository()

# Buscar por email
usuario = usuario_repo.get_by_email("joao@example.com")
print(f"Usuário encontrado: {usuario.email if usuario else 'Não encontrado'}")

# Verificar se email existe
existe = usuario_repo.email_exists("novo@example.com")
print(f"Email já cadastrado: {existe}")


# ============================================================================
# 5. DENTRO DE UMA ROTA (EXEMPLO)
# ============================================================================

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.security import get_current_user
from app.services.produto_service import ProdutoService

exemplo_router = APIRouter()
produto_service = ProdutoService()


@exemplo_router.get('/produtos/{empresa_id}')
def listar_produtos(empresa_id: int, current_user=Depends(get_current_user)):
    """Lista todos os produtos de uma empresa"""
    # Validar acesso
    if current_user.empresa_id != empresa_id:
        return JSONResponse({'error': 'Acesso negado'}, status_code=403)
    
    # Usar o serviço
    produtos = produto_service.obter_produtos_com_imagens(empresa_id)
    
    # Estruturar resposta
    resultado = []
    for item in produtos:
        resultado.append({
            'id': item['produto'].id,
            'nome': item['produto'].nome,
            'preco': item['produto'].preco,
            'imagem': item['imagem']
        })
    
    return resultado


# ============================================================================
# 6. ESTRUTURA DE RESPOSTA DOS SERVIÇOS
# ============================================================================

"""
Os serviços sempre retornam dicts estruturados:

Sucesso:
{
    'success': True,
    'message': 'Operação realizada com sucesso',
    'data': {...}  # Opcional, dados adicionais
}

Erro:
{
    'success': False,
    'message': 'Descrição do erro'
}
"""

# ============================================================================
# 7. TRATAMENTO DE ERROS
# ============================================================================

from app.services.produto_service import ProdutoService

service = ProdutoService()

# Validação automática
resultado = service.criar_produto(
    empresa_id=1,
    nome="Produto",
    ingredientes="Descrição do produto",
    preco="texto_invalido"  # Vai retornar erro de preço inválido
)

if not resultado['success']:
    print(f"Erro: {resultado['message']}")
    # Tratar erro apropriadamente


# ============================================================================
# DICAS IMPORTANTES
# ============================================================================

"""
1. SEMPRE use os serviços nas rotas, não acesse repositories diretamente
2. Os repositórios devem ser usados internamente pelos serviços
3. Retorne sempre a estrutura de resultado dos serviços
4. Use try-catch nos serviços para tratamento centralizado
5. Adicione validação de entrada ANTES de chamar o serviço
6. Mantenha a lógica de negócio nos serviços, não nas rotas
7. Reutilize serviços entre diferentes blueprints
8. Adicione logging para debug e monitoramento
"""
