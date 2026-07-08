from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db
from app.core.permissions import require_permission
from app.models.usuario import Usuario
from app.schemas.modulo import (
    ModuloResponse,
    ModuloCreate,
    ModuloUpdate,
    ModuloDetalle
)
from app.services.modulo_service import ModuloService
from app.models.permiso import Permiso

router = APIRouter()

# ============================================
# ENDPOINTS DE CRUD PARA MODULOS
# ============================================

# Listar y obtener módulos (permiso: permisos.listar)
@router.get(
    "/",
    response_model=List[ModuloResponse],
    summary="Listar módulos",
    description="Obtiene lista de todos los módulos del sistema"
)
def listar_modulos(
    activos_solo: bool = Query(True, description="Solo módulos activos"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission("permisos.listar"))
):
    return ModuloService.listar_modulos(db, activos_solo=activos_solo)

# Obtener módulo por ID (permiso: permisos.listar)
@router.get(
    "/{modulo_id}",
    response_model=ModuloDetalle,
    summary="Obtener módulo por ID",
    description="Obtiene información de un módulo específico"
)
def obtener_modulo(
    modulo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission("permisos.listar"))
):
    modulo = ModuloService.obtener_modulo_por_id(db, modulo_id)
    total_permisos = db.query(Permiso).filter(Permiso.modulo_id == modulo_id).count()
    
    return ModuloDetalle(
        **modulo.__dict__,
        total_permisos=total_permisos
    )

# Crear módulo (permiso: permisos.crear)
@router.post(
    "/",
    response_model=ModuloResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear módulo",
    description="Crea un nuevo módulo en el sistema (solo Superadmin)"
)
def crear_modulo(
    modulo_data: ModuloCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission("permisos.crear"))
):
    return ModuloService.crear_modulo(db, modulo_data)

# Actualizar módulo (permiso: permisos.crear)
@router.put(
    "/{modulo_id}",
    response_model=ModuloResponse,
    summary="Actualizar módulo",
    description="Actualiza un módulo existente (solo Superadmin)"
)
def actualizar_modulo(
    modulo_id: int,
    modulo_data: ModuloUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission("permisos.crear"))
):
    return ModuloService.actualizar_modulo(db, modulo_id, modulo_data)

# Eliminar módulo (permiso: permisos.crear)
@router.delete(
    "/{modulo_id}",
    response_model=dict,
    summary="Eliminar módulo",
    description="Elimina un módulo del sistema (solo Superadmin)"
)
def eliminar_modulo(
    modulo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission("permisos.eliminar"))
):
    return ModuloService.eliminar_modulo(db, modulo_id)