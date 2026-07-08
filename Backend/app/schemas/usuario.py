from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime
import re

from app.schemas.persona import PersonaResponse


# ============================================
# SCHEMA BASE (campos compartidos)
# ============================================
class UsuarioBase(BaseModel):
    """Campos base compartidos por otros schemas"""
    correo: EmailStr
    
    @field_validator('correo')
    @classmethod
    def validar_correo_no_vacio(cls, v: str) -> str:
        """Valida que el correo no esté vacío"""
        if not v or not v.strip():
            raise ValueError('El correo electrónico no puede estar vacío')
        return v.strip().lower()


# ============================================
# SCHEMA PARA CREAR USUARIO (Registro)
# ============================================
class UsuarioCreate(UsuarioBase):
    contrasena: str = Field(
        ..., 
        min_length=6,
        max_length=72,
        description="Contraseña (mínimo 6 caracteres, mayúsculas, minúsculas, números y símbolos)"
    )
    
    @field_validator('contrasena')
    @classmethod
    def validar_contrasena_segura(cls, v: str) -> str:
        """Valida que la contraseña cumpla con todos los requisitos de seguridad."""
        if not v or not v.strip():
            raise ValueError('La contraseña no puede estar vacía')
        
        v = v.strip()
        
        if len(v) < 6:
            raise ValueError('La contraseña debe tener al menos 6 caracteres')
        
        if len(v) > 72:
            raise ValueError('La contraseña no puede exceder 72 caracteres')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        
        if not re.search(r'\d', v):
            raise ValueError('La contraseña debe contener al menos un número')
        
        if not re.search(r'[@$!%*?&_\-.]', v):
            raise ValueError('La contraseña debe contener al menos un carácter especial (@$!%*?&_-.)')
        
        if ' ' in v:
            raise ValueError('La contraseña no puede contener espacios')
        
        contraseñas_comunes = [
            'Password123!', 'Qwerty123!@', 'Admin123!@#', 
            'Welcome123!', '123456789Aa!', 'Passw0rd!@#'
        ]
        if v in contraseñas_comunes:
            raise ValueError('Esta contraseña es demasiado común. Por favor, usa una contraseña más segura.')
        
        return v


# ============================================
# SCHEMA PARA ACTUALIZAR EMAIL
# ============================================
class CambiarEmail(BaseModel):
    """Datos para cambiar el correo electrónico"""
    contrasena_actual: str = Field(..., description="Contraseña actual para verificar identidad")
    nuevo_correo: EmailStr = Field(..., description="Nuevo correo electrónico")
    
    @field_validator('contrasena_actual')
    @classmethod
    def validar_contrasena_actual(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Debes proporcionar tu contraseña actual')
        return v
    
    @field_validator('nuevo_correo')
    @classmethod
    def validar_nuevo_correo(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('El nuevo correo no puede estar vacío')
        return v.strip().lower()


# ============================================
# SCHEMA PARA CAMBIAR CONTRASEÑA
# ============================================
class CambiarContrasena(BaseModel):
    """Datos para cambiar contraseña con confirmación"""
    contrasena_actual: str = Field(..., description="Contraseña actual del usuario")
    contrasena_nueva: str = Field(
        ..., 
        min_length=6, 
        max_length=72,
        description="Nueva contraseña"
    )
    confirmar_contrasena: str = Field(
        ...,
        min_length=6,
        max_length=72,
        description="Confirmar nueva contraseña"
    )
    
    @field_validator('contrasena_actual')
    @classmethod
    def validar_contrasena_actual_no_vacia(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Debes proporcionar tu contraseña actual')
        return v
    
    @field_validator('contrasena_nueva')
    @classmethod
    def validar_contrasena_nueva_segura(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('La nueva contraseña no puede estar vacía')
        
        v = v.strip()
        
        if len(v) < 6:
            raise ValueError('La nueva contraseña debe tener al menos 6 caracteres')
        
        if len(v) > 72:
            raise ValueError('La nueva contraseña no puede exceder 72 caracteres')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('La nueva contraseña debe contener al menos una letra mayúscula')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('La nueva contraseña debe contener al menos una letra minúscula')
        
        if not re.search(r'\d', v):
            raise ValueError('La nueva contraseña debe contener al menos un número')
        
        if not re.search(r'[@$!%*?&_\-.]', v):
            raise ValueError('La nueva contraseña debe contener al menos un carácter especial (@$!%*?&_-.)')
        
        if ' ' in v:
            raise ValueError('La nueva contraseña no puede contener espacios')
        
        return v
    
    @field_validator('confirmar_contrasena')
    @classmethod
    def validar_confirmacion(cls, v: str, info) -> str:
        if not v or not v.strip():
            raise ValueError('Debes confirmar tu nueva contraseña')
        
        contrasena_nueva = info.data.get('contrasena_nueva')
        
        if contrasena_nueva and v.strip() != contrasena_nueva:
            raise ValueError('Las contraseñas no coinciden')
        
        return v.strip()


# ============================================
# SCHEMA PARA VALIDACIÓN DE EMAIL
# ============================================
class ValidarEmail(BaseModel):
    """Datos para validar email"""
    token: str = Field(..., min_length=1, description="Token de validación recibido por correo")
    
    @field_validator('token')
    @classmethod
    def validar_token_no_vacio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('El token no puede estar vacío')
        return v.strip()


# ============================================
# SCHEMA PARA REENVIAR VALIDACIÓN
# ============================================
class ReenviarValidacion(BaseModel):
    """Datos para reenviar email de validación"""
    correo: EmailStr
    
    @field_validator('correo')
    @classmethod
    def validar_correo_reenvio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('El correo electrónico no puede estar vacío')
        return v.strip().lower()


# ============================================
# SCHEMA DE RESPUESTA (lo que devuelve la API)
# ============================================
class UsuarioResponse(UsuarioBase):
    """
    Datos que se devuelven al cliente.
    """
    id: int
    correo_validado: bool
    perfil_completo: bool
    estado: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)





# ============================================
# SCHEMA DE MENSAJE GENÉRICO
# ============================================
class MensajeResponse(BaseModel):
    """Respuesta genérica con un mensaje"""
    mensaje: str


# ============================================
# SCHEMA PARA SOLICITAR RECUPERACIÓN DE CONTRASEÑA
# ============================================
class SolicitarRecuperacionContrasena(BaseModel):
    """Datos para solicitar recuperación de contraseña"""
    correo: EmailStr
    
    @field_validator('correo')
    @classmethod
    def validar_correo_recuperacion(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('El correo electrónico no puede estar vacío')
        return v.strip().lower()

# ============================================
# SCHEMA ROL SIMPLE (para anidar en usuario)
# ============================================
class RolSimple(BaseModel):
    """Rol simplificado para incluir en respuesta de usuario"""
    id: int
    nombre: str
    descripcion: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================
# SCHEMA RESPUESTA CON ROLES
# ============================================
class UsuarioConRoles(UsuarioResponse):
    """
    Usuario con sus roles incluidos.
    Se usa en el listado admin para evitar N+1 queries.
    """
    roles: List[RolSimple] = []

    model_config = ConfigDict(from_attributes=True)


# ============================================
# SCHEMA PAGINADO
# ============================================
class UsuariosPaginados(BaseModel):
    """Respuesta paginada de usuarios"""
    items: List[UsuarioConRoles]
    total: int
    page: int
    limit: int
    pages: int



# ============================================
# SCHEMA DETALLADO
# ============================================
class UsuarioDetalle(UsuarioResponse):
    """
    Información detallada del usuario CON perfil Y roles.
    Se usa en endpoints como /usuarios/me y /usuarios/admin/{id}
    """
    eliminado_at: Optional[datetime] = None
    persona: Optional[PersonaResponse] = None
    roles: List[RolSimple] = []         

    model_config = ConfigDict(from_attributes=True)

# ============================================
# SCHEMA PARA RESTABLECER CONTRASEÑA CON CONFIRMACIÓN
# ============================================
class RestablecerContrasenaConfirmacion(BaseModel):
    """Datos para restablecer contraseña con confirmación"""
    token: str = Field(..., min_length=1, description="Token de recuperación recibido por correo")
    contrasena_nueva: str = Field(..., min_length=6, max_length=72, description="Nueva contraseña")
    confirmar_contrasena: str = Field(..., min_length=6, max_length=72, description="Confirmar nueva contraseña")
    
    @field_validator('token')
    @classmethod
    def validar_token_no_vacio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('El token no puede estar vacío')
        return v.strip()
    
    @field_validator('contrasena_nueva')
    @classmethod
    def validar_contrasena_nueva_segura(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('La nueva contraseña no puede estar vacía')
        
        v = v.strip()
        
        if len(v) < 6:
            raise ValueError('La nueva contraseña debe tener al menos 6 caracteres')
        
        if len(v) > 72:
            raise ValueError('La nueva contraseña no puede exceder 72 caracteres')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('La nueva contraseña debe contener al menos una letra mayúscula')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('La nueva contraseña debe contener al menos una letra minúscula')
        
        if not re.search(r'\d', v):
            raise ValueError('La nueva contraseña debe contener al menos un número')
        
        if not re.search(r'[@$!%*?&_\-.]', v):
            raise ValueError('La nueva contraseña debe contener al menos un carácter especial (@$!%*?&_-.)')
        
        if ' ' in v:
            raise ValueError('La nueva contraseña no puede contener espacios')
        
        return v
    
    @field_validator('confirmar_contrasena')
    @classmethod
    def validar_confirmacion(cls, v: str, info) -> str:
        if not v or not v.strip():
            raise ValueError('Debes confirmar tu nueva contraseña')
        
        contrasena_nueva = info.data.get('contrasena_nueva')
        
        if contrasena_nueva and v.strip() != contrasena_nueva:
            raise ValueError('Las contraseñas no coinciden')
        
        return v.strip()