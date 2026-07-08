from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from typing import List, Optional 
from app.api.deps import get_db, get_current_active_user, get_current_user_with_profile
from app.core.permissions import require_permission
# Agregar a los imports existentes al inicio del archivo
from app.schemas.usuario import (
    UsuarioResponse,
    UsuarioDetalle,
    UsuarioConRoles,      
    UsuariosPaginados,     
    CambiarContrasena,
    CambiarEmail,
    MensajeResponse
)
from app.schemas.persona import PersonaCreate, PersonaUpdate, PersonaResponse
from app.services.usuario_service import UsuarioService
from app.services.persona_service import PersonaService
from app.models.usuario import Usuario


router = APIRouter()


# ============================================
# ENDPOINTS DEL USUARIO AUTENTICADO (MI CUENTA)
# ============================================

@router.get(
    "/me",
    response_model=UsuarioDetalle,
    summary="Obtener mi información completa",
    description="Obtiene la información del usuario autenticado + su perfil (persona)"
)
def obtener_mi_info(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    return UsuarioService.obtener_usuario_completo(db, current_user.id)


@router.get(
    "/me/verificar-perfil",
    response_model=dict,
    summary="Verificar si tengo perfil completo",
    description="Verifica si el usuario tiene perfil completo y retorna qué falta"
)
def verificar_mi_perfil(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    from app.repositories.persona import PersonaRepository
    
    persona = PersonaRepository.get_by_usuario_id(db, current_user.id)
    
    return {
        "perfil_completo": current_user.perfil_completo,
        "tiene_perfil": persona is not None,
        "correo_validado": current_user.correo_validado,
        "mensaje": "Perfil completo" if current_user.perfil_completo else 
                   "Debes completar tu perfil para acceder a todas las funcionalidades" if not persona else
                   "Tu perfil está incompleto"
    }


@router.post(
    "/me/perfil",
    response_model=PersonaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear/Completar mi perfil",
    description="Crea el perfil (persona) asociado al usuario autenticado"
)
def crear_mi_perfil(
    perfil_data: PersonaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    return PersonaService.crear_perfil_usuario(db, current_user.id, perfil_data)

@router.get(
    "/me/perfil",
    response_model=PersonaResponse,
    summary="Obtener mi perfil",
    description="Devuelve el perfil asociado al usuario autenticado"
)
def obtener_mi_perfil(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    return PersonaService.obtener_perfil_usuario(db, current_user.id)

@router.put(
    "/me/perfil",
    response_model=PersonaResponse,
    summary="Actualizar mi perfil",
    description="Actualiza los datos de perfil (nombre, documento, etc.)"
)
def actualizar_mi_perfil(
    perfil_data: PersonaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    return PersonaService.actualizar_perfil_usuario(db, current_user.id, perfil_data)


@router.put(
    "/me/email",
    response_model=MensajeResponse,
    summary="Cambiar mi correo electrónico",
    description="Cambia el correo del usuario (requiere validación)"
)
def cambiar_mi_email(
    email_data: CambiarEmail,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    return UsuarioService.cambiar_email(db, current_user.id, email_data)


@router.put(
    "/me/password",
    response_model=MensajeResponse,
    summary="Cambiar mi contraseña",
    description="Cambia la contraseña del usuario autenticado"
)
def cambiar_mi_contrasena(
    contrasena_data: CambiarContrasena,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    return UsuarioService.cambiar_contrasena(db, current_user.id, contrasena_data)


@router.delete(
    "/me",
    response_model=MensajeResponse,
    summary="Eliminar mi cuenta",
    description="Elimina lógicamente la cuenta del usuario autenticado (soft delete)"
)
def eliminar_mi_cuenta(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Elimina la cuenta (soft delete):
    - Los datos NO se borran físicamente
    - Se puede reactivar si el usuario vuelve a registrarse
    """
    return UsuarioService.eliminar_usuario(db, current_user.id)


# ============================================
# Endpoint que REQUIERE perfil completo
# ============================================

@router.get(
    "/me/sacramentos",
    response_model=list,
    summary="Ver mis sacramentos",
    description="Lista los sacramentos del usuario (REQUIERE PERFIL COMPLETO)"
)
def obtener_mis_sacramentos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_with_profile)
):
    # TODO: 
    return []


# ============================================
# ENDPOINTS ADMINISTRATIVOS (ADMIN)
# ============================================

# Listar usuarios, requiere permiso "usuarios.listar"
@router.get(
    "/admin/list",
    response_model=UsuariosPaginados,
    summary="Listar usuarios (Admin)",
    description="Lista usuarios con filtros por estado, rol y búsqueda por correo"
)
def listar_usuarios_admin(
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(20, ge=1, le=100, description="Usuarios por página"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    rol_id: Optional[int] = Query(None, description="Filtrar por rol"),
    buscar: Optional[str] = Query(None, description="Buscar por correo"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission("usuarios.listar"))
):
    from app.repositories.usuario import UsuarioRepository
    from app.models.rol import Rol
    from app.models.usuario_rol import UsuarioRol

    skip = (page - 1) * limit

    usuarios = UsuarioRepository.get_all(
        db,
        skip=skip,
        limit=limit,
        estado=estado,
        buscar=buscar,
        rol_id=rol_id,
    )

    total = UsuarioRepository.count(
        db,
        estado=estado,
        buscar=buscar,
        rol_id=rol_id,
    )

    # Cargar roles para cada usuario eficientemente
    import math
    resultado = []
    for u in usuarios:
        roles = (
            db.query(Rol)
            .join(UsuarioRol, UsuarioRol.rol_id == Rol.id)
            .filter(
                UsuarioRol.usuario_id == u.id,
                UsuarioRol.activo == True
            )
            .all()
        )
        u_dict = {
            "id": u.id,
            "correo": u.correo,
            "correo_validado": u.correo_validado,
            "perfil_completo": u.perfil_completo,
            "estado": u.estado,
            "created_at": u.created_at,
            "updated_at": u.updated_at,
            "roles": [{"id": r.id, "nombre": r.nombre, "descripcion": r.descripcion} for r in roles],
        }
        resultado.append(u_dict)

    return {
        "items": resultado,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": math.ceil(total / limit) if total > 0 else 1,
    }

# Obtener usuario específico, requiere permiso "usuarios.ver"
@router.get(
    "/admin/{usuario_id}",
    response_model=UsuarioDetalle,
    summary="Ver usuario específico (Admin)",
    description="Obtiene información detallada de un usuario incluyendo roles"
)
def obtener_usuario_admin(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission("usuarios.ver"))
):
    from app.models.rol import Rol
    from app.models.usuario_rol import UsuarioRol

    usuario = UsuarioService.obtener_usuario_completo(db, usuario_id)

    # Cargar roles del usuario
    roles = (
        db.query(Rol)
        .join(UsuarioRol, UsuarioRol.rol_id == Rol.id)
        .filter(
            UsuarioRol.usuario_id == usuario_id,
            UsuarioRol.activo == True
        )
        .all()
    )

    # UsuarioDetalle es un objeto Pydantic — construir con roles
    usuario_dict = {
        "id":               usuario.id,
        "correo":           usuario.correo,
        "correo_validado":  usuario.correo_validado,
        "perfil_completo":  usuario.perfil_completo,
        "estado":           usuario.estado,
        "created_at":       usuario.created_at,
        "updated_at":       usuario.updated_at,
        "eliminado_at":     getattr(usuario, 'eliminado_at', None),
        "persona":          usuario.persona if hasattr(usuario, 'persona') else None,
        "roles": [
            {"id": r.id, "nombre": r.nombre, "descripcion": r.descripcion}
            for r in roles
        ],
    }

    return usuario_dict

# Eliminar usuario, requiere permiso "usuarios.eliminar" (soft delete)
@router.delete(
    "/admin/{usuario_id}",
    response_model=MensajeResponse,
    summary="Eliminar usuario (Admin)",
    description="Elimina lógicamente un usuario"
)
def eliminar_usuario_admin(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission("usuarios.eliminar"))
):
    return UsuarioService.eliminar_usuario(db, usuario_id)


# Validar cambio de correo, necesita token de validación (enviado por correo) para confirmar el cambio de email
@router.get(
    "/validar-cambio-correo",
    response_model=MensajeResponse,
    summary="Validar cambio de correo",
    description="Valida el nuevo correo y efectúa el cambio"
)
def validar_cambio_correo(
    token: str = Query(..., description="Token de validación recibido por correo"),
    db: Session = Depends(get_db)
):
    return UsuarioService.validar_cambio_correo(db, token)