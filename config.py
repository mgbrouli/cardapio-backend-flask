"""Configurações compartilhadas da aplicação."""

import os
from dotenv import load_dotenv

load_dotenv()

BASEDIR = os.path.abspath(os.path.dirname(__file__))
DEFAULT_SECRET_KEY = "uma-chave-muito-segura-e-secreta-123"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", DEFAULT_SECRET_KEY)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASEDIR, "banco.db")
    )
    ASAAS_API_KEY = os.environ.get("ASAAS_API_KEY", "")
    ASAAS_SANDBOX = os.environ.get("ASAAS_SANDBOX", "True").lower() == "true"
    ASAAS_BASE_URL = (
        "https://sandbox.asaas.com/api/v3"
        if ASAAS_SANDBOX
        else "https://api.asaas.com/v3"
    )
    WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config():
    """Retorna as configurações correspondentes ao ambiente."""
    environment = os.environ.get("APP_ENV", "development")
    return config.get(environment, config["default"])
