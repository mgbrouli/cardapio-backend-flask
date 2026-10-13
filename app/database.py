"""Configuração SQLAlchemy independente de frameworks web."""

from contextvars import ContextVar
from threading import get_ident

from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    create_engine,
)
from sqlalchemy.orm import backref, declarative_base, relationship, scoped_session, sessionmaker
from sqlalchemy.pool import StaticPool

request_scope = ContextVar("database_request_scope", default=None)


def _scope_key():
    return request_scope.get() or ("thread", get_ident())


class Database:
    Model = declarative_base()
    Column = Column
    Integer = Integer
    String = String
    Float = Float
    Boolean = Boolean
    LargeBinary = LargeBinary
    ForeignKey = ForeignKey
    relationship = staticmethod(relationship)
    backref = staticmethod(backref)

    def __init__(self):
        self.engine = None
        self.session = scoped_session(
            sessionmaker(expire_on_commit=False), scopefunc=_scope_key
        )

    def configure(self, database_url):
        if self.engine is not None and str(self.engine.url) == database_url:
            return
        self.session.remove()
        if self.engine is not None:
            self.engine.dispose()
        is_sqlite = database_url.startswith("sqlite")
        connect_args = {"check_same_thread": False} if is_sqlite else {}
        engine_options = {}
        if database_url in {"sqlite://", "sqlite:///:memory:"}:
            engine_options["poolclass"] = StaticPool
        self.engine = create_engine(
            database_url, connect_args=connect_args, **engine_options
        )
        self.session.configure(bind=self.engine)

    def create_all(self):
        self.Model.metadata.create_all(bind=self.engine)


db = Database()
db.Model.query = db.session.query_property()
