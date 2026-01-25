"""Base repository com operações CRUD genéricas"""
from app.models import db


class BaseRepository:
    """Classe base com operações CRUD comuns"""
    
    def __init__(self, model):
        self.model = model
    
    def create(self, **kwargs):
        """Cria uma nova entidade"""
        try:
            entity = self.model(**kwargs)
            db.session.add(entity)
            db.session.commit()
            return entity
        except Exception as e:
            db.session.rollback()
            raise e
    
    def get_by_id(self, id):
        """Busca entidade pelo ID"""
        return self.model.query.get(id)
    
    def get_all(self):
        """Retorna todas as entidades"""
        return self.model.query.all()
    
    def update(self, entity, **kwargs):
        """Atualiza uma entidade"""
        try:
            for key, value in kwargs.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            db.session.commit()
            return entity
        except Exception as e:
            db.session.rollback()
            raise e
    
    def delete(self, entity):
        """Deleta uma entidade"""
        try:
            db.session.delete(entity)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    def flush(self):
        """Faz flush sem commit (útil para gerar IDs)"""
        try:
            db.session.flush()
        except Exception as e:
            db.session.rollback()
            raise e
