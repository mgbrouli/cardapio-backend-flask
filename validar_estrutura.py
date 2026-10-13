#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Validação da Nova Estrutura
Verifica se todos os componentes estão corretos
"""

import os
import sys

# Cores para output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
END = '\033[0m'


def print_header(text):
    print(f"\n{BLUE}{'='*60}{END}")
    print(f"{BLUE}{text}{END}")
    print(f"{BLUE}{'='*60}{END}\n")


def check_file(filepath):
    """Verifica se um arquivo existe"""
    if os.path.exists(filepath):
        print(f"{GREEN}✓{END} {filepath}")
        return True
    else:
        print(f"{RED}✗{END} {filepath} (FALTA)")
        return False


def check_directory(dirpath):
    """Verifica se um diretório existe"""
    if os.path.isdir(dirpath):
        print(f"{GREEN}✓{END} {dirpath}/")
        return True
    else:
        print(f"{RED}✗{END} {dirpath}/ (FALTA)")
        return False


def check_import(module_name):
    """Verifica se um módulo pode ser importado"""
    try:
        __import__(module_name)
        print(f"{GREEN}✓{END} {module_name}")
        return True
    except ImportError as e:
        print(f"{RED}✗{END} {module_name} - {str(e)}")
        return False


def main():
    basedir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(basedir)
    
    print_header("VALIDAÇÃO DA ESTRUTURA DO PROJETO")
    
    all_ok = True
    
    # 1. Verificar diretórios
    print(f"{YELLOW}1. Verificando diretórios...{END}")
    dirs_to_check = [
        'app',
        'app/models',
        'app/repositories',
        'app/services',
        'app/routes',
        'app/utils',
        'static',
        'templates'
    ]
    for dir_path in dirs_to_check:
        if not check_directory(dir_path):
            all_ok = False
    
    # 2. Verificar arquivos principais
    print(f"\n{YELLOW}2. Verificando arquivos principais...{END}")
    files_to_check = [
        'app.py',
        'config.py',
        'banco.db',
        'requirements.txt'
    ]
    for file_path in files_to_check:
        if not check_file(file_path):
            all_ok = False
    
    # 3. Verificar models
    print(f"\n{YELLOW}3. Verificando models...{END}")
    model_files = [
        'app/models/__init__.py'
    ]
    for file_path in model_files:
        if not check_file(file_path):
            all_ok = False
    
    # 4. Verificar repositories
    print(f"\n{YELLOW}4. Verificando repositories...{END}")
    repo_files = [
        'app/repositories/__init__.py',
        'app/repositories/base_repository.py',
        'app/repositories/produto_repository.py',
        'app/repositories/imagem_repository.py',
        'app/repositories/empresa_repository.py',
        'app/repositories/usuario_repository.py'
    ]
    for file_path in repo_files:
        if not check_file(file_path):
            all_ok = False
    
    # 5. Verificar services
    print(f"\n{YELLOW}5. Verificando services...{END}")
    service_files = [
        'app/services/__init__.py',
        'app/services/produto_service.py',
        'app/services/empresa_service.py',
        'app/services/auth_service.py'
    ]
    for file_path in service_files:
        if not check_file(file_path):
            all_ok = False
    
    # 6. Verificar routes
    print(f"\n{YELLOW}6. Verificando routes...{END}")
    routes_files = [
        'app/routes/__init__.py',
        'app/routes/public_routes.py',
        'app/routes/auth_routes.py',
        'app/routes/produto_routes.py',
        'app/routes/empresa_routes.py'
    ]
    for file_path in routes_files:
        if not check_file(file_path):
            all_ok = False
    
    # 7. Verificar utils
    print(f"\n{YELLOW}7. Verificando utils...{END}")
    if not check_file('app/utils/__init__.py'):
        all_ok = False
    
    # 8. Verificar documentação
    print(f"\n{YELLOW}8. Verificando documentação...{END}")
    doc_files = [
        'README_ESTRUTURA.md',
        'ARQUITETURA.md',
        'GUIA_RAPIDO.md',
        'EXEMPLOS_USO.py',
        'ESTRUTURA_FINAL.md',
        'RESUMO_FINAL.txt'
    ]
    for file_path in doc_files:
        if not check_file(file_path):
            all_ok = False
    
    # 9. Verificar imports
    print(f"\n{YELLOW}9. Verificando imports...{END}")
    imports_to_check = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'argon2',
        'multipart'
    ]
    for module in imports_to_check:
        check_import(module)
    
    # 10. Resultado final
    print_header("RESULTADO FINAL")
    
    if all_ok:
        print(f"{GREEN}{'✓ TUDO ESTÁ OK!'}{END}")
        print(f"\n{GREEN}Sua estrutura está pronta para uso!{END}")
        print(f"{BLUE}Próximos passos:{END}")
        print(f"  1. Leia: README_ESTRUTURA.md")
        print(f"  2. Entenda: ARQUITETURA.md")
        print(f"  3. Consulte: GUIA_RAPIDO.md")
        print(f"  4. Execute: python run.py")
        return 0
    else:
        print(f"{RED}{'✗ EXISTEM PROBLEMAS!'}{END}")
        print(f"\n{YELLOW}Verifique os erros acima e corrija.{END}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
