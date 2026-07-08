from fastapi import HTTPException
from fastapi import APIRouter, Depends, status, Query, Request
from sqlalchemy.orm import Session
from typing import List
import logging
from datetime import datetime, timezone
from app.schemas.usuario import ReenviarValidacion

from app.api.deps import get_db, get_current_active_user, get_session_token
from app.schemas.auth import (
    LoginRequest, 
    Token, 
    RefreshTokenRequest,
    SesionInfo,
    LogoutRequest
)
from app.schemas.usuario import (
    UsuarioCreate, 
    UsuarioResponse, 
    ValidarEmail, 
    ReenviarValidacion,
    MensajeResponse,
    SolicitarRecuperacionContrasena,
    RestablecerContrasenaConfirmacion
)
from app.services.auth_service import AuthService
from app.services.usuario_service import UsuarioService
from app.models.usuario import Usuario
from app.repositories.usuario import UsuarioRepository
from app.utils.tokens import token_expirado

router = APIRouter()
logger = logging.getLogger(__name__)

# REGISTRO DE USUARIO
@router.post(
    "/register",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
    description="Crea una cuenta de usuario nueva y envía email de validación"
)
def registrar_usuario(
    usuario_data: UsuarioCreate,
    db: Session = Depends(get_db)
):
    return UsuarioService.crear_usuario(db, usuario_data)

# VALIDAR EMAIL (POST)
@router.post(
    "/validar-email",
    response_model=MensajeResponse,
    summary="Validar correo electrónico (POST)",
    description="Valida el correo usando el token enviado por email"
)
def validar_email_post(
    validacion_data: ValidarEmail,
    db: Session = Depends(get_db)
):
    usuario = UsuarioService.validar_email(db, validacion_data.token)
    return MensajeResponse(
        mensaje=f"¡Correo validado exitosamente! Ya puedes iniciar sesión con: {usuario.correo}"
    )

# VALIDAR EMAIL (GET)
@router.get(
    "/validar-email",
    response_model=MensajeResponse,
    summary="Validar correo electrónico (GET)",
    description="Valida el correo usando el token como query parameter"
)
def validar_email_get(
    token: str = Query(..., description="Token de validación recibido por email"),
    db: Session = Depends(get_db)
):
    usuario = UsuarioService.validar_email(db, token)
    return MensajeResponse(
        mensaje=f"¡Correo validado exitosamente! Ya puedes iniciar sesión con: {usuario.correo}"
    )

# REENVIAR EMAIL DE VALIDACIÓN
@router.post(
    "/reenviar-validacion",
    response_model=MensajeResponse,
    summary="Reenviar email de validación",
    description="Envía un nuevo email de validación si el anterior expiró"
)
def reenviar_validacion(
    reenvio_data: ReenviarValidacion,
    db: Session = Depends(get_db)
):
    resultado = UsuarioService.reenviar_email_validacion(db, reenvio_data.correo)
    return MensajeResponse(mensaje=resultado["mensaje"])

# LOGIN (Autenticación)
@router.post(
    "/login",
    response_model=Token,
    summary="Iniciar sesión",
    description="Autentica un usuario y devuelve access + refresh tokens"
)
def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    return AuthService.login(db, login_data, request)

# REFRESH TOKEN (Renovar access token)
@router.post(
    "/refresh",
    response_model=Token,
    summary="Renovar access token",
    description="Obtiene un nuevo access token usando el refresh token"
)
def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Renueva el access token cuando este expira.
    
    **Flujo:**
    1. El cliente detecta que el access token expiró (error 401)
    2. Envía el refresh token a este endpoint
    3. Recibe un nuevo access token
    4. Continúa haciendo peticiones normalmente
    
    **Nota:** El refresh token permanece igual, solo se renueva el access token.
    """
    return AuthService.refresh_access_token(db, refresh_data)

# LOGOUT (Cerrar sesión)
@router.post(
    "/logout",
    response_model=MensajeResponse,
    summary="Cerrar sesión",
    description="Cierra la sesión actual o todas las sesiones del usuario"
)
def logout(
    logout_data: LogoutRequest,
    db: Session = Depends(get_db),
    session_token: str = Depends(get_session_token),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Cierra sesión revocando los tokens.
    cerrar_todas=false: Cierra solo esta sesión (predeterminado)
    cerrar_todas=true: Cierra todas las sesiones activas del usuario
    Después del logout, los tokens quedan inválidos.
    """
    result = AuthService.logout(
        db=db,
        session_token=session_token,
        cerrar_todas=logout_data.cerrar_todas,
        usuario_id=current_user.id
    )
    return MensajeResponse(mensaje=result["mensaje"])

# LISTAR SESIONES ACTIVAS
@router.get(
    "/sesiones",
    response_model=List[SesionInfo],
    summary="Listar sesiones activas",
    description="Obtiene todas las sesiones activas del usuario autenticado"
)
def listar_sesiones_activas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    return AuthService.listar_sesiones_activas(db, current_user.id)

# RECUPERACIÓN DE CONTRASEÑA
@router.post(
    "/forgot-password",
    response_model=MensajeResponse,
    status_code=status.HTTP_200_OK,
    summary="Olvidé mi contraseña",
    description="Solicita un token de recuperación de contraseña por correo electrónico"
)
def solicitar_recuperacion_contrasena(
    datos: SolicitarRecuperacionContrasena,
    db: Session = Depends(get_db)
):
    return UsuarioService.solicitar_recuperacion_contrasena(db, datos.correo)

# RESTABLECER CONTRASEÑA (GET)

@router.get(
    "/reset-password",
    response_model=MensajeResponse,
    summary="Verificar token de recuperación",
    description="Endpoint GET para cuando el usuario hace clic en el enlace del correo"
)
def verificar_token_reset(
    token: str = Query(..., description="Token de recuperación"),
    db: Session = Depends(get_db)
):
    
    usuario = UsuarioRepository.get_by_token_recuperacion(db, token)

    if not usuario:
        logger.error(f"No se encontró usuario con token: {token[:20]}...")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de recuperación inválido o ya ha sido usado"
        )
    
    if token_expirado(usuario.token_expiracion):
        logger.error(f"Token expirado para {usuario.correo}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El token de recuperación ha expirado. Solicita uno nuevo."
        )
    
    return MensajeResponse(
        mensaje=f"Token válido para {usuario.correo}. Usa el endpoint POST /reset-password-confirm para establecer tu nueva contraseña."
    )

# RESTABLECER CONTRASEÑA
@router.post(
    "/reset-password-confirm",
    response_model=MensajeResponse,
    status_code=status.HTTP_200_OK,
    summary="Restablecer contraseña (con confirmación)",
    description="Restablece la contraseña validando que coincidan"
)
def restablecer_contrasena_confirmacion(
    datos: RestablecerContrasenaConfirmacion,
    db: Session = Depends(get_db)
):
    return UsuarioService.restablecer_contrasena_con_confirmacion(
        db,
        datos.token,
        datos.contrasena_nueva,
        datos.confirmar_contrasena
    )


@router.post(
    "/reactivar-cuenta",
    response_model=MensajeResponse,
    summary="Reactivar cuenta eliminada",
    description="Reactiva una cuenta eliminada y envía email de validación"
)
def reactivar_cuenta(
    datos: ReenviarValidacion,   # reutilizar el schema {correo}
    db: Session = Depends(get_db)
):
    UsuarioService.reactivar_cuenta(db, datos.correo)
    return MensajeResponse(
        mensaje="Cuenta reactivada. Revisa tu correo para validarla "
                "y luego usa 'Olvidé mi contraseña' para establecer una nueva."
    )