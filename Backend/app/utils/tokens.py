import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from app.core.config import settings

# Funciones para generar y validar tokens de validación de email
def generar_token_validacion() -> str:
    return secrets.token_urlsafe(32)

# Función para calcular la fecha de expiración del token
def calcular_expiracion_token() -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=settings.EMAIL_TOKEN_EXPIRE_HOURS)

# Función para verificar si el token ha expirado
def token_expirado(fecha_expiracion: Optional[datetime]) -> bool:
    if fecha_expiracion is None:
        return True
    
    # Usar datetime con timezone
    ahora = datetime.now(timezone.utc)
    
    # Si fecha_expiracion no tiene timezone, añadirla
    if fecha_expiracion.tzinfo is None:
        fecha_expiracion = fecha_expiracion.replace(tzinfo=timezone.utc)
    
    return ahora > fecha_expiracion