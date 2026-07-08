"""
Schemas de la aplicación.
"""

from app.schemas.usuario import (
    UsuarioCreate,
    UsuarioResponse,
    UsuarioDetalle,
    CambiarContrasena,
    CambiarEmail,
    ValidarEmail,
    ReenviarValidacion,
    MensajeResponse,
    SolicitarRecuperacionContrasena,
    RestablecerContrasenaConfirmacion
)

from app.schemas.persona import (
    PersonaCreate,
    PersonaUpdate,
    PersonaResponse
)

from app.schemas.auth import (
    LoginRequest,
    Token,
    RefreshTokenRequest,
    SesionInfo,
    LogoutRequest
)

from app.schemas.rol import (
    RolCreate,
    RolUpdate,
    RolResponse,
    RolDetalle
)

from app.schemas.permiso import (
    PermisoCreate,
    PermisoResponse
)

from app.schemas.modulo import (
    ModuloCreate,
    ModuloUpdate,
    ModuloResponse
)

__all__ = [
    # Usuario
    "UsuarioCreate",
    "UsuarioResponse",
    "UsuarioDetalle",
    "CambiarContrasena",
    "CambiarEmail",
    "ValidarEmail",
    "ReenviarValidacion",
    "MensajeResponse",
    "SolicitarRecuperacionContrasena",
    "RestablecerContrasenaConfirmacion",
    
    # Persona
    "PersonaCreate",
    "PersonaUpdate",
    "PersonaResponse",
    
    # Auth
    "LoginRequest",
    "Token",
    "RefreshTokenRequest",
    "SesionInfo",
    "LogoutRequest",
    
    # Rol
    "RolCreate",
    "RolUpdate",
    "RolResponse",
    "RolDetalle",
    
    # Permiso
    "PermisoCreate",
    "PermisoResponse",
    
    # Modulo
    "ModuloCreate",
    "ModuloUpdate",
    "ModuloResponse"
]