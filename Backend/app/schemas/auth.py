from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class LoginRequest(BaseModel):
    correo: EmailStr
    contrasena: str

# Clase para la respuesta del token, incluyendo información adicional del usuario y la sesión
class Token(BaseModel):
    access_token:    str
    refresh_token:   str
    token_type:      str  = "bearer"
    expires_in:      int       
    session_token:   str
    usuario_id:      Optional[int]  = None
    perfil_completo: bool           = False
    correo_validado: bool           = True
    estado:          Optional[str]  = None
    persona_id:      Optional[int]  = None
    roles:           List[str]      = []


class TokenData(BaseModel):
    correo:        Optional[str] = None
    session_token: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class SesionInfo(BaseModel):
    id:                int
    session_token:     str
    ip_address:        Optional[str]
    user_agent:        Optional[str]
    dispositivo:       Optional[str]
    fecha_creacion:    datetime
    fecha_ultimo_uso:  datetime
    fecha_expiracion:  datetime
    activa:            bool

    class Config:
        from_attributes = True


class LogoutRequest(BaseModel):
    cerrar_todas: bool = False