from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.api.deps import get_db, get_current_user, get_current_active_user, get_current_user_with_profile
from app.models.usuario import Usuario
from app.schemas.solicitud import (
    SolicitudSacramentoCreate,
    SolicitudSacramentoUpdate,
    SolicitudSacramentoOut,
    PaginatedSolicitudes,
    CambiarEstadoSolicitud,
    ValidarPersonaSolicitudRequest,
)
from app.services import solicitud_service
from app.repositories.usuario_rol import UsuarioRolRepository

router = APIRouter(tags=["Solicitudes de Sacramento"])


# ─────────────────────────────────────────────
# HELPERS DE PERMISOS
# ─────────────────────────────────────────────

def _es_admin(db: Session, usuario: Usuario) -> bool:
    roles_usuario = UsuarioRolRepository.get_roles_usuario(db, usuario.id)
    nombres_roles = [r.nombre.lower().strip() for r in roles_usuario if hasattr(r, 'nombre')]
    roles_admin = ["administrador parroquial", "párroco", "parroco", "superadmin", "secretario", "secretaria", "admin"]
    return any(
        any(admin_r in user_r or user_r in admin_r for user_r in nombres_roles)
        for admin_r in roles_admin
    )


def _require_admin(db: Session, usuario: Usuario) -> None:
    if not _es_admin(db, usuario):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para esta acción"
        )


# ─────────────────────────────────────────────
# USUARIO — Crear solicitud
# ─────────────────────────────────────────────

@router.post(
    "/",
    response_model=SolicitudSacramentoOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear solicitud de sacramento"
)
def crear_solicitud(
    payload: SolicitudSacramentoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_with_profile)
):
    return solicitud_service.crear_solicitud(
        db=db,
        usuario_id=current_user.id,
        sacramento_id=payload.sacramento_id,
        personas_data=payload.personas,
        fecha_preferida=payload.fecha_preferida,
        hora_preferida=payload.hora_preferida,
        motivo=payload.motivo,
        observaciones=payload.observaciones
    )


# ─────────────────────────────────────────────
# USUARIO — Mis solicitudes
# ─────────────────────────────────────────────

@router.get(
    "/mis-solicitudes",
    response_model=PaginatedSolicitudes,
    summary="Listar mis solicitudes"
)
def mis_solicitudes(
    pagina: int = Query(1, ge=1),
    por_pagina: int = Query(10, ge=1, le=50),
    estado: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return solicitud_service.listar_mis_solicitudes(
        db=db,
        usuario_id=current_user.id,
        pagina=pagina,
        por_pagina=por_pagina,
        estado=estado
    )


# ─────────────────────────────────────────────
# ADMIN — Listar todas (DEBE IR ANTES de /{solicitud_id})
# ─────────────────────────────────────────────

@router.get(
    "/admin/todas",
    response_model=PaginatedSolicitudes,
    summary="[ADMIN] Listar todas las solicitudes"
)
def listar_todas(
    pagina: int = Query(1, ge=1),
    por_pagina: int = Query(10, ge=1, le=100),
    estado: Optional[str] = Query(None),
    sacramento_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    _require_admin(db, current_user)
    return solicitud_service.listar_todas_solicitudes(
        db=db,
        pagina=pagina,
        por_pagina=por_pagina,
        estado=estado,
        sacramento_id=sacramento_id
    )


# ─────────────────────────────────────────────
# USUARIO — Ver detalle (DESPUÉS de rutas estáticas)
# ─────────────────────────────────────────────

@router.get(
    "/{solicitud_id}",
    response_model=SolicitudSacramentoOut,
    summary="Detalle de una solicitud"
)
def detalle_solicitud(
    solicitud_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    admin = _es_admin(db, current_user)
    return solicitud_service.obtener_solicitud(
        db=db,
        solicitud_id=solicitud_id,
        usuario_id=current_user.id,
        es_admin=admin
    )


# ─────────────────────────────────────────────
# USUARIO — Actualizar solicitud
# ─────────────────────────────────────────────

@router.patch(
    "/{solicitud_id}",
    response_model=SolicitudSacramentoOut,
    summary="Actualizar solicitud (usuario)"
)
def actualizar_solicitud(
    solicitud_id: int,
    payload: SolicitudSacramentoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return solicitud_service.actualizar_solicitud(
        db=db,
        solicitud_id=solicitud_id,
        usuario_id=current_user.id,
        datos=payload.model_dump(exclude_none=True)
    )


# ─────────────────────────────────────────────
# USUARIO — Cancelar solicitud
# ─────────────────────────────────────────────

@router.post(
    "/{solicitud_id}/cancelar",
    response_model=SolicitudSacramentoOut,
    summary="Cancelar solicitud"
)
def cancelar_solicitud(
    solicitud_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return solicitud_service.cancelar_solicitud(
        db=db,
        solicitud_id=solicitud_id,
        usuario_id=current_user.id
    )


# ─────────────────────────────────────────────
# USUARIO — Subir documento
# ─────────────────────────────────────────────

@router.post(
    "/{solicitud_id}/documentos",
    summary="Subir documento a una solicitud"
)
async def subir_documento(
    solicitud_id: int,
    file: UploadFile = File(...),
    tipo_documento: str = Form(...),
    categoria: str = Form(...),
    persona_id: Optional[int] = Form(None),
    descripcion: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    admin = _es_admin(db, current_user)
    return await solicitud_service.subir_documento_solicitud(
        db=db,
        solicitud_id=solicitud_id,
        usuario_id=current_user.id,
        file=file,
        tipo_documento=tipo_documento,
        categoria=categoria,
        persona_id=persona_id,
        descripcion=descripcion,
        es_admin=admin
    )


# ─────────────────────────────────────────────
# ADMIN — Cambiar estado
# ─────────────────────────────────────────────

@router.patch(
    "/{solicitud_id}/estado",
    response_model=SolicitudSacramentoOut,
    summary="[ADMIN] Cambiar estado de solicitud"
)
def cambiar_estado(
    solicitud_id: int,
    payload: CambiarEstadoSolicitud,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    _require_admin(db, current_user)
    return solicitud_service.cambiar_estado_solicitud(
        db=db,
        solicitud_id=solicitud_id,
        nuevo_estado=payload.estado.value,
        revisor_id=current_user.id,
        observaciones_secretario=payload.observaciones_secretario
    )


# ─────────────────────────────────────────────
# ADMIN — Validar persona en solicitud
# ─────────────────────────────────────────────

@router.patch(
    "/{solicitud_id}/personas/{persona_id}/validar",
    summary="[ADMIN] Validar datos de persona en solicitud"
)
def validar_persona(
    solicitud_id: int,
    persona_id: int,
    rol: str = Query(..., description="Rol de la persona en la solicitud"),
    payload: ValidarPersonaSolicitudRequest = ...,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    _require_admin(db, current_user)
    return solicitud_service.validar_persona_en_solicitud(
        db=db,
        solicitud_id=solicitud_id,
        persona_id=persona_id,
        rol=rol,
        datos_validados=payload.datos_validados,
        revisor_id=current_user.id,
        observaciones=payload.observaciones_validacion
    )