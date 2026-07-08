from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db
from app.core.permissions import require_permission, get_user_permissions
from app.models.usuario import Usuario
from app.schemas.permiso import (
    PermisoResponse,
    PermisoCreate,
    PermisoUpdate,
    PermisoDetalle,
    AsignarPermisosRol,
    AsignarPermisosUsuario,
    MisPermisosResponse
)
from app.services.permiso_service import PermisoService

router = APIRouter()

# ── RUTAS FIJAS primero (antes de /{id}) ──────────────────

@router.get(
    "/mis-permisos",
    response_model=MisPermisosResponse,
    summary="Ver mis permisos"
)
def obtener_mis_permisos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission("usuarios.ver_propios"))
):
    permisos_codigos = get_user_permissions(db, current_user.id)
    return MisPermisosResponse(
        usuario_id=current_user.id,
        correo=current_user.correo,
        permisos=permisos_codigos,
        total=len(permisos_codigos)
    )


@router.get(
    "/por-modulo/{modulo_id}",
    response_model=List[PermisoResponse],
    summary="Listar permisos por módulo"
)
def listar_permisos_por_modulo(
    modulo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission("permisos.listar"))
):
    return PermisoService.listar_permisos_por_modulo(db, modulo_id)


@router.get(
    "/rol/{rol_id}",
    response_model=List[PermisoResponse],
    summary="Ver permisos de un rol"
)
def obtener_permisos_de_rol(
    rol_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission("roles.asignar_permisos"))
):
    return PermisoService.obtener_permisos_de_rol(db, rol_id)


@router.post(
    "/rol/{rol_id}/asignar",
    response_model=dict,
    summary="Asignar permisos a un rol"
)
def asignar_permisos_a_rol(
    rol_id: int,
    permisos_data: AsignarPermisosRol,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission("roles.asignar_permisos"))
):
    return PermisoService.asignar_permisos_a_rol(
        db, rol_id, permisos_data.permisos_ids
    )


@router.delete(
    "/rol/{rol_id}/permiso/{permiso_id}",
    response_model=dict,
    summary="Remover permiso de un rol"
)
def remover_permiso_de_rol(
    rol_id: int,
    permiso_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission("roles.asignar_permisos"))
):
    return PermisoService.remover_permiso_de_rol(db, rol_id, permiso_id)


@router.get(
    "/usuario/{usuario_id}",
    response_model=List[PermisoResponse],
    summary="Ver permisos de un usuario"
)
def obtener_permisos_de_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission("usuarios.ver"))
):
    return PermisoService.obtener_permisos_de_usuario(db, usuario_id)


@router.get(
    "/usuario/{usuario_id}/directos",
    response_model=List[PermisoResponse],
    summary="Ver permisos directos de un usuario"
)
def obtener_permisos_directos_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission("usuarios.asignar_roles"))
):
    return PermisoService.obtener_permisos_directos_usuario(db, usuario_id)


@router.post(
    "/usuario/{usuario_id}/asignar",
    response_model=dict,
    summary="Asignar permisos directos a un usuario"
)
def asignar_permisos_directos_usuario(
    usuario_id: int,
    permisos_data: AsignarPermisosUsuario,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission("usuarios.asignar_roles"))
):
    return PermisoService.asignar_permisos_directos_bulk(
        db, usuario_id, permisos_data.permisos_ids
    )


@router.delete(
    "/usuario/{usuario_id}/permiso/{permiso_id}",
    response_model=dict,
    summary="Remover permiso directo de un usuario"
)
def remover_permiso_directo_usuario(
    usuario_id: int,
    permiso_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission("usuarios.asignar_roles"))
):
    return PermisoService.remover_permiso_directo_usuario(
        db, usuario_id, permiso_id
    )


# ── RUTAS CON {id} al final (después de las fijas) ────────

@router.get(
    "/",
    response_model=List[PermisoResponse],
    summary="Listar permisos"
)
def listar_permisos(
    activos_solo: bool = Query(False, description="Solo permisos activos"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission("permisos.listar"))
):
    return PermisoService.listar_permisos(db, activos_solo=activos_solo)


@router.post(
    "/",
    response_model=PermisoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear permiso"
)
def crear_permiso(
    permiso_data: PermisoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission("permisos.crear"))
):
    return PermisoService.crear_permiso(db, permiso_data)


@router.get(
    "/{permiso_id}",
    response_model=PermisoDetalle,
    summary="Obtener permiso por ID"
)
def obtener_permiso(
    permiso_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission("permisos.listar"))
):
    return PermisoService.obtener_permiso_por_id(db, permiso_id)


@router.put(
    "/{permiso_id}",
    response_model=PermisoResponse,
    summary="Actualizar permiso"
)
def actualizar_permiso(
    permiso_id: int,
    permiso_data: PermisoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission("permisos.crear"))
):
    permiso = PermisoService.obtener_permiso_por_id(db, permiso_id)

    if permiso_data.nombre is not None:
        permiso.nombre = permiso_data.nombre
    if permiso_data.descripcion is not None:
        permiso.descripcion = permiso_data.descripcion
    if permiso_data.activo is not None:
        permiso.activo = permiso_data.activo

    db.commit()
    db.refresh(permiso)
    return permiso