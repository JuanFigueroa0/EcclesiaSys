from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db
from app.core.permissions import require_permission
from app.models.usuario import Usuario
from app.schemas.rol import (
    RolResponse,
    RolCreate,
    RolUpdate,
    RolDetalle,
    AsignarRolUsuario
)
from app.schemas.usuario import UsuarioResponse
from app.services.rol_service import RolService
from app.models.usuario_rol import UsuarioRol
from app.models.rol_permiso import RolPermiso
    

router = APIRouter()


# ============================================
# ENDPOINTS CRUD DE ROLES
# ============================================

# Obtener lista roles, requiere permiso "roles.listar" (READ)
@router.get(
    "/",
    response_model=List[RolResponse],
    summary="Listar roles",
    description="Obtiene lista de todos los roles del sistema"
)
def listar_roles(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission("roles.listar"))
):
    return RolService.listar_roles(db)

# Listar rol por ID, requiere permiso "roles.ver" (READ)
@router.get(
    "/{rol_id}",
    response_model=RolDetalle,
    summary="Listar rol por ID",
    description="Obtiene información de un rol específico"
)
def obtener_rol(
    rol_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission("roles.ver"))
):
    rol = RolService.obtener_rol_por_id(db, rol_id)
    
    total_usuarios = db.query(UsuarioRol).filter(
        UsuarioRol.rol_id == rol_id,
        UsuarioRol.activo == True
    ).count()
    
    total_permisos = db.query(RolPermiso).filter(
        RolPermiso.rol_id == rol_id
    ).count()
    
    return RolDetalle(
        **rol.__dict__,
        total_usuarios=total_usuarios,
        total_permisos=total_permisos
    )

# Obtener usuarios por rol, requiere permiso "usuarios.listar" (READ)
@router.get(
    "/{rol_id}/usuarios",
    response_model=List[UsuarioResponse],
    summary="Obtener usuarios por rol",
    description="Obtiene todos los usuarios que tienen un rol específico"
)
def obtener_usuarios_por_rol(
    rol_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission("usuarios.listar"))
):
    return RolService.obtener_usuarios_por_rol(db, rol_id)

# Crear rol, requiere permiso "roles.crear" (CREATE)    
@router.post(
    "/",
    response_model=RolResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear rol",
    description="Crea un nuevo rol en el sistema (solo Superadmin)"
)
def crear_rol(
    rol_data: RolCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission("roles.crear"))
):
    return RolService.crear_rol(db, rol_data)

# Actualizar rol, requiere permiso "roles.editar" (UPDATE)
@router.put(
    "/{rol_id}",
    response_model=RolResponse,
    summary="Actualizar rol",
    description="Actualiza un rol existente (solo Superadmin)"
)
def actualizar_rol(
    rol_id: int,
    rol_data: RolUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission("roles.editar"))
):
    return RolService.actualizar_rol(db, rol_id, rol_data)

# Eliminar rol, requiere permiso "roles.eliminar" (DELETE)
@router.delete(
    "/{rol_id}",
    response_model=dict,
    summary="Eliminar rol",
    description="Elimina un rol del sistema (solo Superadmin)"
)
def eliminar_rol(
    rol_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission("roles.eliminar"))
):
    return RolService.eliminar_rol(db, rol_id)

# Asignar rol a usuario, requiere permiso "usuarios.asignar_roles" (UPDATE)
@router.post(
    "/asignar-usuario",
    response_model=dict,
    summary="Asignar rol a usuario",
    description="Asigna un rol a un usuario específico"
)
def asignar_rol_a_usuario(
    asignacion: AsignarRolUsuario,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission("usuarios.asignar_roles"))
):
    return RolService.asignar_rol_a_usuario(
        db,
        asignacion.usuario_id,
        asignacion.rol_id
    )

# Remover rol de usuario, requiere permiso "usuarios.asignar_roles" (UPDATE)
@router.delete(
    "/remover-usuario/{usuario_id}/{rol_id}",
    response_model=dict,
    summary="Remover rol de usuario",
    description="Remueve un rol de un usuario específico"
)
def remover_rol_de_usuario(
    usuario_id: int,
    rol_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission("usuarios.asignar_roles"))
):
    return RolService.remover_rol_de_usuario(db, usuario_id, rol_id)