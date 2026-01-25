"""Arquivo de configuração da aplicação"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Diretório base
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Configurações base"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'uma-chave-muito-segura-e-secreta-123')
    
    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(basedir, 'banco.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Flask-Login
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    
    # Asaas - Integração de Pagamentos (desativado por enquanto)
    ASAAS_API_KEY = os.environ.get('ASAAS_API_KEY', '')
    ASAAS_SANDBOX = os.environ.get('ASAAS_SANDBOX', 'True').lower() == 'true'
    # ASAAS_BASE_URL será definida no __init__ da aplicação quando necessário
    
    # Webhook
    WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', '')


class DevelopmentConfig(Config):
    """Configurações de desenvolvimento"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Configurações de produção"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Configurações de testes"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Seleção de configuração
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Retorna a configuração apropriada"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
