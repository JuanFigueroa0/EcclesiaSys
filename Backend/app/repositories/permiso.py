from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.permiso import Permiso


class PermisoRepository:
    """
    Repositorio para operaciones CRUD de permisos.
    """
    
    @staticmethod
    def get_by_id(db: Session, permiso_id: int) -> Optional[Permiso]:
        """Busca un permiso por ID"""
        return db.query(Permiso).filter(Permiso.id == permiso_id).first()
    
    @staticmethod
    def get_by_codigo(db: Session, codigo: str) -> Optional[Permiso]:
        """Busca un permiso por código (ej: usuarios.listar)"""
        return db.query(Permiso).filter(Permiso.codigo == codigo).first()
    
    @staticmethod
    def get_by_codigos(db: Session, codigos: List[str]) -> List[Permiso]:
        """Busca múltiples permisos por sus códigos"""
        return db.query(Permiso).filter(Permiso.codigo.in_(codigos)).all()
    
    @staticmethod
    def get_all(db: Session, activos_solo: bool = True) -> List[Permiso]:
        """Obtiene todos los permisos"""
        query = db.query(Permiso)
        if activos_solo:
            query = query.filter(Permiso.activo == True)
        return query.all()
    
    @staticmethod
    def create(
        db: Session,
        codigo: str,
        nombre: str,
        descripcion: str = None,
        modulo_id: int = None
    ) -> Permiso:
        """Crea un nuevo permiso"""
        permiso = Permiso(
            codigo=codigo,
            nombre=nombre,
            descripcion=descripcion,
            modulo_id=modulo_id
        )
        db.add(permiso)
        db.commit()
        db.refresh(permiso)
        return permiso
    
    @staticmethod
    def create_bulk(db: Session, permisos_data: List[dict]) -> List[Permiso]:
        
        """Crea múltiples permisos a la vez. Evita duplicados por código."""
        permisos = []
        for data in permisos_data:
            # Verificar si ya existe
            existe = db.query(Permiso).filter(Permiso.codigo == data['codigo']).first()
            if not existe:
                permiso = Permiso(**data)
                db.add(permiso)
                permisos.append(permiso)
        
        db.commit()
        return permisos