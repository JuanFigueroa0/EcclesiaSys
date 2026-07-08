from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
import secrets
from .config import settings
from fastapi import HTTPException, status

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================
# HASHING
# ============================================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ============================================
# ACCESS TOKEN
# ============================================

def create_access_token(
    data: dict,
    session_token: str,
    expires_delta: Optional[timedelta] = None,
    # Identidad
    usuario_id: Optional[int] = None,
    perfil_completo: bool = False,
    correo_validado: bool = True,
    estado: Optional[str] = None,
    # Persona vinculada
    persona_id: Optional[int] = None,
    # Roles
    roles: Optional[List[str]] = None
) -> str:
    to_encode = data.copy()

    expire = (
        datetime.now(timezone.utc) + expires_delta
        if expires_delta
        else datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    to_encode.update({
        "exp":             expire,
        "session_token":   session_token,
        "type":            "access",
        # Identidad
        "usuario_id":      usuario_id,
        "perfil_completo": perfil_completo,
        "correo_validado": correo_validado,
        "estado":          estado,
        # Persona
        "persona_id":      persona_id,
        # Roles
        "roles":           roles or [],
    })

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


# ============================================
# REFRESH TOKEN
# ============================================

def create_refresh_token(
    usuario_id: int,
    session_token: str
) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    to_encode = {
        "sub":           str(usuario_id),
        "session_token": session_token,
        "exp":           expire,
        "type":          "refresh"
    }

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


# ============================================
# DECODIFICAR TOKENS
# ============================================

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None


def decode_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None


def generar_session_token() -> str:
    return secrets.token_urlsafe(32)


# ============================================
# VERIFY TOKEN (usado en deps)
# ============================================

def verify_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )