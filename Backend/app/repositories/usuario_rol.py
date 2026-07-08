from sqlalchemy.orm import Session
from typing import List

from app.models.usuario_rol import UsuarioRol
from app.models.rol import Rol
from app.models.usuario import Usuario


class UsuarioRolRepository:
    """
    Repositorio para la relación usuario-rol.
    """
    
    @staticmethod
    def asignar_rol(
        db: Session,
        usuario_id: int,
        rol_id: int,
        activo: bool = True,
        sincronizar_permisos: bool = True   # ← nuevo parámetro
    ) -> UsuarioRol:
        """Asigna un rol a un usuario y opcionalmente sincroniza permisos."""
        relacion_existente = db.query(UsuarioRol).filter(
            UsuarioRol.usuario_id == usuario_id,
            UsuarioRol.rol_id == rol_id
        ).first()

        if relacion_existente:
            relacion_existente.activo = activo
            db.commit()
            db.refresh(relacion_existente)
            resultado = relacion_existente
        else:
            usuario_rol = UsuarioRol(
                usuario_id=usuario_id,
                rol_id=rol_id,
                activo=activo
            )
            db.add(usuario_rol)
            db.commit()
            db.refresh(usuario_rol)
            resultado = usuario_rol

        # Sincronizar permisos automáticamente si se pide
        if sincronizar_permisos and activo:
            from app.repositories.usuario_permiso import UsuarioPermisoRepository
            UsuarioPermisoRepository.sincronizar_permisos_desde_rol(
                db=db,
                usuario_id=usuario_id,
                rol_id=rol_id
            )

        return resultado

    @staticmethod
    def remover_rol(
        db: Session,
        usuario_id: int,
        rol_id: int
    ) -> bool:
        """Desactiva un rol de un usuario y sus permisos asociados."""
        usuario_rol = db.query(UsuarioRol).filter(
            UsuarioRol.usuario_id == usuario_id,
            UsuarioRol.rol_id == rol_id
        ).first()

        if usuario_rol:
            usuario_rol.activo = False
            db.commit()

            # También desactivar permisos que venían de este rol
            from app.repositories.usuario_permiso import UsuarioPermisoRepository
            UsuarioPermisoRepository.desactivar_permisos_de_rol(
                db=db,
                usuario_id=usuario_id,
                rol_id=rol_id
            )
            return True

        return False
    @staticmethod
    def remover_rol(
        db: Session,
        usuario_id: int,
        rol_id: int
    ) -> bool:
        """Desactiva un rol de un usuario."""
        usuario_rol = db.query(UsuarioRol).filter(
            UsuarioRol.usuario_id == usuario_id,
            UsuarioRol.rol_id == rol_id
        ).first()
        
        if usuario_rol:
            usuario_rol.activo = False
            db.commit()
            return True
        
        return False
    
    @staticmethod
    def get_roles_usuario(db: Session, usuario_id: int) -> List[Rol]:
        """Obtiene todos los roles activos de un usuario."""
        return db.query(Rol).join(UsuarioRol).filter(
            UsuarioRol.usuario_id == usuario_id,
            UsuarioRol.activo == True
        ).all()
    
    @staticmethod
    def usuario_tiene_rol(
        db: Session,
        usuario_id: int,
        nombre_rol: str
    ) -> bool:
        """Verifica si un usuario tiene un rol específico."""   
        return db.query(UsuarioRol).join(Rol).filter(
            UsuarioRol.usuario_id == usuario_id,
            UsuarioRol.activo == True,
            Rol.nombre == nombre_rol
        ).first() is not None
    
    @staticmethod
    def get_usuarios_por_rol(db: Session, rol_id: int) -> List[Usuario]:
        """
        Obtiene todos los usuarios que tienen un rol específico.
        Retorna objetos Usuario completos.
        """
        usuarios = db.query(Usuario).join(UsuarioRol).filter(
            UsuarioRol.rol_id == rol_id,
            UsuarioRol.activo == True,
            Usuario.eliminado_at.is_(None)
        ).all()
        
        return usuarios