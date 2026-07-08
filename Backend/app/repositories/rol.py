from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.rol import Rol


class RolRepository:
    """
    Repositorio para operaciones CRUD de roles.
    """
    
    @staticmethod
    def get_by_id(db: Session, rol_id: int) -> Optional[Rol]:
        """Busca un rol por ID"""
        return db.query(Rol).filter(Rol.id == rol_id).first()
    
    @staticmethod
    def get_by_nombre(db: Session, nombre: str) -> Optional[Rol]:
        """Busca un rol por nombre"""
        return db.query(Rol).filter(Rol.nombre == nombre).first()
    
    @staticmethod
    def get_all(db: Session) -> List[Rol]:
        """Obtiene todos los roles"""
        return db.query(Rol).order_by(Rol.nombre).all()
    
    @staticmethod
    def create(
        db: Session,
        nombre: str,
        descripcion: str = None,
        es_sistema: bool = False
    ) -> Rol:
        """Crea un nuevo rol"""
        rol = Rol(
            nombre=nombre,
            descripcion=descripcion,
            es_sistema=es_sistema
        )
        db.add(rol)
        db.commit()
        db.refresh(rol)
        return rol
    
    @staticmethod
    def update(db: Session, rol: Rol, **kwargs) -> Rol:
        """Actualiza un rol"""
        for key, value in kwargs.items():
            if hasattr(rol, key) and value is not None:
                setattr(rol, key, value)
        
        db.commit()
        db.refresh(rol)
        return rol
    
    @staticmethod
    def delete(db: Session, rol: Rol) -> None:
        """Elimina un rol"""
        db.delete(rol)
        db.commit()