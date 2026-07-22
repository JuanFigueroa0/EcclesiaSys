from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.models.usuario import Usuario
from app.repositories.usuario import UsuarioRepository
from app.repositories.sesion import SesionRepository

# Conexión a la base de datos
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# SEGURIDAD: HTTPBearer para JWT
security = HTTPBearer()

# Obtener usuario actual
def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # Extraer token de las credenciales
    token = credentials.credentials
    
    # Decodificar token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado. Por favor renueva tu token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extraer correo y session_token del token
    correo: str = payload.get("sub")
    session_token: str = payload.get("session_token")
    
    if correo is None or session_token is None:
        raise credentials_exception
    
    #VERIFICAR QUE LA SESIÓN ESTÉ ACTIVA
    sesion = SesionRepository.get_by_session_token(db, session_token)
    
    if not sesion:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión inválida o expirada. Por favor inicia sesión nuevamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Buscar usuario en BD
    usuario = UsuarioRepository.get_by_correo(db, correo=correo)
    if usuario is None:
        raise credentials_exception
    
    # Verificar que el usuario esté activo
    if usuario.estado and usuario.estado.lower() != 'activo':
        # Revocar sesión si el usuario no está activo
        SesionRepository.revocar_sesion(db, sesion, "Usuario inactivo")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo o pendiente de validación"
        )
    
    # ACTUALIZAR FECHA DE ÚLTIMO USO
    SesionRepository.actualizar_ultimo_uso(db, sesion)
    
    return usuario

# Verificar que el usuario esté activo
def get_current_active_user(
    current_user: Usuario = Depends(get_current_user)   
) -> Usuario:
    if current_user.eliminado_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    return current_user

# Verificar que el perfil del usuario esté completo
def get_current_user_with_profile(
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Usuario:
    if not current_user.perfil_completo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debes completar tu perfil de usuario antes de radicar solicitudes."
        )
    return current_user


# Obtener session_token del access token (logout)
def get_session_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    session_token = payload.get("session_token")
    
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token malformado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return session_token