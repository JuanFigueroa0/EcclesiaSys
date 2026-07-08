from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.modulo import Modulo


class ModuloRepository:
    """
    Repositorio para operaciones CRUD de módulos.
    """
    
    @staticmethod
    def get_by_id(db: Session, modulo_id: int) -> Optional[Modulo]:
        """Busca un módulo por ID"""
        return db.query(Modulo).filter(Modulo.id == modulo_id).first()
    
    @staticmethod
    def get_by_codigo(db: Session, codigo: str) -> Optional[Modulo]:
        """Busca un módulo por código"""
        return db.query(Modulo).filter(Modulo.codigo == codigo).first()
    
    @staticmethod
    def get_by_nombre(db: Session, nombre: str) -> Optional[Modulo]:
        """Busca un módulo por nombre"""
        return db.query(Modulo).filter(Modulo.nombre == nombre).first()
    
    @staticmethod
    def get_all(db: Session, activos_solo: bool = True) -> List[Modulo]:
        """Obtiene todos los módulos"""
        query = db.query(Modulo)
        if activos_solo:
            query = query.filter(Modulo.activo == True)
        return query.order_by(Modulo.nombre).all()
    
    @staticmethod
    def create(
        db: Session,
        nombre: str,
        codigo: str,
        descripcion: str = None
    ) -> Modulo:
        """Crea un nuevo módulo"""
        modulo = Modulo(
            nombre=nombre,
            codigo=codigo,
            descripcion=descripcion
        )
        db.add(modulo)
        db.commit()
        db.refresh(modulo)
        return modulo
    
    @staticmethod
    def update(db: Session, modulo: Modulo, **kwargs) -> Modulo:
        """Actualiza un módulo"""
        for key, value in kwargs.items():
            if hasattr(modulo, key) and value is not None:
                setattr(modulo, key, value)
        
        db.commit()
        db.refresh(modulo)
        return modulo
    
    @staticmethod
    def delete(db: Session, modulo: Modulo) -> None:
        """Elimina un módulo"""
        db.delete(modulo)
        db.commit()