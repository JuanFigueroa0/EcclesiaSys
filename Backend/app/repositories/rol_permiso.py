from sqlalchemy.orm import Session
from typing import List
from app.models.rol_permiso import RolPermiso
from app.models.permiso import Permiso
from app.models.modulo import Modulo
from app.models.usuario_rol import UsuarioRol
from app.models.rol import Rol


class RolPermisoRepository:

    @staticmethod
    def asignar_permiso(db: Session, rol_id: int, permiso_id: int) -> RolPermiso:
        existe = db.query(RolPermiso).filter(
            RolPermiso.rol_id == rol_id,
            RolPermiso.permiso_id == permiso_id
        ).first()
        if existe:
            return existe
        rol_permiso = RolPermiso(rol_id=rol_id, permiso_id=permiso_id)
        db.add(rol_permiso)
        db.commit()
        db.refresh(rol_permiso)
        return rol_permiso

    @staticmethod
    def asignar_permisos_bulk(
        db: Session, rol_id: int, permisos_ids: List[int]
    ) -> List[RolPermiso]:
        relaciones = []
        for permiso_id in permisos_ids:
            relacion = RolPermisoRepository.asignar_permiso(db, rol_id, permiso_id)
            relaciones.append(relacion)
        return relaciones

    @staticmethod
    def remover_permiso(db: Session, rol_id: int, permiso_id: int) -> bool:
        rol_permiso = db.query(RolPermiso).filter(
            RolPermiso.rol_id == rol_id,
            RolPermiso.permiso_id == permiso_id
        ).first()
        if rol_permiso:
            db.delete(rol_permiso)
            db.commit()
            return True
        return False

    @staticmethod
    def _base_query_permisos_activos(db: Session):
        """
        Query base que devuelve solo permisos activos
        cuyo módulo también está activo.
        """
        return (
            db.query(Permiso)
            .outerjoin(Modulo, Modulo.id == Permiso.modulo_id)
            .filter(
                Permiso.activo == True,
                # Si tiene módulo, el módulo debe estar activo
                # Si no tiene módulo (modulo_id NULL), se permite igual
                (Modulo.activo == True) | (Permiso.modulo_id == None)
            )
        )

    @staticmethod
    def get_permisos_por_rol(db: Session, rol_id: int) -> List[Permiso]:
        """Permisos activos de un rol (filtra módulos inactivos)."""
        return (
            RolPermisoRepository._base_query_permisos_activos(db)
            .join(RolPermiso, RolPermiso.permiso_id == Permiso.id)
            .filter(RolPermiso.rol_id == rol_id)
            .all()
        )

    @staticmethod
    def get_permisos_por_usuario(db: Session, usuario_id: int) -> List[Permiso]:
        """
        Permisos activos de un usuario a través de sus roles.
        Filtra: permiso inactivo, módulo inactivo, rol inactivo.
        """
        return (
            RolPermisoRepository._base_query_permisos_activos(db)
            .distinct()
            .join(RolPermiso, RolPermiso.permiso_id == Permiso.id)
            .join(Rol, Rol.id == RolPermiso.rol_id)
            .join(UsuarioRol, UsuarioRol.rol_id == Rol.id)
            .filter(
                UsuarioRol.usuario_id == usuario_id,
                UsuarioRol.activo == True,
            )
            .all()
        )

    @staticmethod
    def usuario_tiene_permiso(
        db: Session, usuario_id: int, codigo_permiso: str
    ) -> bool:
        existe = (
            RolPermisoRepository._base_query_permisos_activos(db)
            .join(RolPermiso, RolPermiso.permiso_id == Permiso.id)
            .join(Rol, Rol.id == RolPermiso.rol_id)
            .join(UsuarioRol, UsuarioRol.rol_id == Rol.id)
            .filter(
                UsuarioRol.usuario_id == usuario_id,
                UsuarioRol.activo == True,
                Permiso.codigo == codigo_permiso,
            )
            .first()
        )
        return existe is not None

    @staticmethod
    def usuario_tiene_cualquier_permiso(
        db: Session, usuario_id: int, codigos_permisos: List[str]
    ) -> bool:
        existe = (
            RolPermisoRepository._base_query_permisos_activos(db)
            .join(RolPermiso, RolPermiso.permiso_id == Permiso.id)
            .join(Rol, Rol.id == RolPermiso.rol_id)
            .join(UsuarioRol, UsuarioRol.rol_id == Rol.id)
            .filter(
                UsuarioRol.usuario_id == usuario_id,
                UsuarioRol.activo == True,
                Permiso.codigo.in_(codigos_permisos),
            )
            .first()
        )
        return existe is not None

    @staticmethod
    def usuario_tiene_todos_permisos(
        db: Session, usuario_id: int, codigos_permisos: List[str]
    ) -> bool:
        count = (
            RolPermisoRepository._base_query_permisos_activos(db)
            .distinct()
            .join(RolPermiso, RolPermiso.permiso_id == Permiso.id)
            .join(Rol, Rol.id == RolPermiso.rol_id)
            .join(UsuarioRol, UsuarioRol.rol_id == Rol.id)
            .filter(
                UsuarioRol.usuario_id == usuario_id,
                UsuarioRol.activo == True,
                Permiso.codigo.in_(codigos_permisos),
            )
            .count()
        )
        return count == len(codigos_permisos)