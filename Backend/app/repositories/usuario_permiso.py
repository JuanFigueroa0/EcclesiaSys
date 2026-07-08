from sqlalchemy.orm import Session
from typing import List

from app.models.usuario_permiso import UsuarioPermiso
from app.models.rol_permiso import RolPermiso
from app.models.permiso import Permiso


class UsuarioPermisoRepository:
    """
    Repositorio para permisos directos de usuario (usuario_permiso).
    Se usan para copiar los permisos del rol asignado al usuario.
    """

    @staticmethod
    def sincronizar_permisos_desde_rol(
        db: Session,
        usuario_id: int,
        rol_id: int
    ) -> List[UsuarioPermiso]:
        """
        Copia todos los permisos activos de un rol a usuario_permiso.
        Si el permiso ya existe para el usuario, lo activa (no duplica).
        """
        # Obtener permisos activos del rol
        permisos_del_rol = (
            db.query(RolPermiso.permiso_id)
            .join(Permiso, Permiso.id == RolPermiso.permiso_id)
            .filter(
                RolPermiso.rol_id == rol_id,
                Permiso.activo == True
            )
            .all()
        )

        permisos_ids = [p.permiso_id for p in permisos_del_rol]
        registros = []

        for permiso_id in permisos_ids:
            # Verificar si ya existe
            existente = db.query(UsuarioPermiso).filter(
                UsuarioPermiso.usuario_id == usuario_id,
                UsuarioPermiso.permiso_id == permiso_id
            ).first()

            if existente:
                if not existente.activo:
                    existente.activo = True
                registros.append(existente)
            else:
                nuevo = UsuarioPermiso(
                    usuario_id=usuario_id,
                    permiso_id=permiso_id,
                    activo=True
                )
                db.add(nuevo)
                registros.append(nuevo)

        db.commit()
        return registros

    @staticmethod
    def get_permisos_usuario(
        db: Session,
        usuario_id: int
    ) -> List[UsuarioPermiso]:
        """Retorna todos los permisos activos directos del usuario."""
        return db.query(UsuarioPermiso).filter(
            UsuarioPermiso.usuario_id == usuario_id,
            UsuarioPermiso.activo == True
        ).all()

    @staticmethod
    def desactivar_permisos_de_rol(
        db: Session,
        usuario_id: int,
        rol_id: int
    ) -> int:
        """
        Desactiva permisos de usuario que venían de un rol específico.
        Útil cuando se remueve un rol al usuario.
        """
        permisos_del_rol = (
            db.query(RolPermiso.permiso_id)
            .filter(RolPermiso.rol_id == rol_id)
            .all()
        )
        permisos_ids = [p.permiso_id for p in permisos_del_rol]
        count = 0

        for permiso_id in permisos_ids:
            registro = db.query(UsuarioPermiso).filter(
                UsuarioPermiso.usuario_id == usuario_id,
                UsuarioPermiso.permiso_id == permiso_id,
                UsuarioPermiso.activo == True
            ).first()
            if registro:
                registro.activo = False
                count += 1

        db.commit()
        return count