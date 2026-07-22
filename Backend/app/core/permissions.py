# Backend/app/core/permissions.py
from typing import List
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.models.usuario import Usuario
from app.repositories.rol_permiso import RolPermisoRepository
from app.repositories.usuario_rol import UsuarioRolRepository


# ============================================
# FUNCIÓN CENTRAL: obtener TODOS los permisos
# ============================================

def get_user_permissions(db: Session, usuario_id: int) -> List[str]:
    """
    Obtiene TODOS los permisos efectivos de un usuario:
    1. Permisos heredados por sus roles
    2. Permisos asignados directamente al usuario

    Retorna lista de códigos únicos (sin duplicados).
    """
    # 1. Permisos por rol (ya existía)
    permisos_por_rol = RolPermisoRepository.get_permisos_por_usuario(db, usuario_id)
    codigos = {p.codigo for p in permisos_por_rol}

    # 2. Permisos directos (nueva tabla usuario_permiso)
    try:
        from app.models.usuario_permiso import UsuarioPermiso
        from app.models.permiso import Permiso

        permisos_directos = (
            db.query(Permiso)
            .join(UsuarioPermiso, UsuarioPermiso.permiso_id == Permiso.id)
            .filter(
                UsuarioPermiso.usuario_id == usuario_id,
                UsuarioPermiso.activo == True,
                Permiso.activo == True,
            )
            .all()
        )
        for p in permisos_directos:
            codigos.add(p.codigo)
    except Exception:
        # Si la tabla aún no existe, ignorar silenciosamente
        pass

    return list(codigos)


def check_permission(db: Session, usuario_id: int, codigo_permiso: str) -> bool:
    """
    Verifica si un usuario tiene un permiso específico.
    Considera tanto permisos por rol como permisos directos.
    """
    # Superadmin y Admin bypass
    roles_usuario  = UsuarioRolRepository.get_roles_usuario(db, usuario_id)
    nombres_roles  = [rol.nombre.lower() for rol in roles_usuario if hasattr(rol, 'nombre')]
    roles_bypass   = ["superadmin", "administrador parroquial", "párroco", "parroco", "admin"]
    if any(any(b in r for r in nombres_roles) for b in roles_bypass):
        return True

    # Verificar en permisos efectivos combinados
    todos = get_user_permissions(db, usuario_id)
    return codigo_permiso in todos


# ============================================
# CLASE: Verificador de permisos (dependencia FastAPI)
# ============================================

class RequirePermissions:
    def __init__(
        self,
        permisos: List[str],
        require_all: bool = False,
        allow_superadmin_bypass: bool = True
    ):
        self.permisos              = permisos
        self.require_all           = require_all
        self.allow_superadmin_bypass = allow_superadmin_bypass

    def __call__(
        self,
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(get_current_active_user)
    ) -> Usuario:

        # Superadmin / Admin bypass
        if self.allow_superadmin_bypass:
            roles_usuario = UsuarioRolRepository.get_roles_usuario(db, current_user.id)
            nombres_roles = [rol.nombre.lower() for rol in roles_usuario if hasattr(rol, 'nombre')]
            roles_bypass   = ["superadmin", "administrador parroquial", "párroco", "parroco", "admin"]
            if any(any(b in r for r in nombres_roles) for b in roles_bypass):
                return current_user

        # Obtener todos los permisos efectivos del usuario
        permisos_usuario = set(get_user_permissions(db, current_user.id))

        if self.require_all:
            tiene = all(p in permisos_usuario for p in self.permisos)
            msg   = f"Requieres TODOS: {', '.join(self.permisos)}"
        else:
            tiene = any(p in permisos_usuario for p in self.permisos)
            msg   = f"Requieres al menos uno de: {', '.join(self.permisos)}"

        if not tiene:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=msg
            )

        return current_user


# ============================================
# ALIAS CONVENIENTES
# ============================================

def require_permission(permiso: str, allow_superadmin_bypass: bool = False):
    return RequirePermissions(
        [permiso], require_all=True,
        allow_superadmin_bypass=allow_superadmin_bypass
    )

def require_any_permission(permisos: List[str], allow_superadmin_bypass: bool = False):
    return RequirePermissions(
        permisos, require_all=False,
        allow_superadmin_bypass=allow_superadmin_bypass
    )

def require_all_permissions(permisos: List[str], allow_superadmin_bypass: bool = False):
    return RequirePermissions(
        permisos, require_all=True,
        allow_superadmin_bypass=allow_superadmin_bypass
    )