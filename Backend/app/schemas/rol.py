from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# ============================================
# SCHEMA BASE
# ============================================
class RolBase(BaseModel):
    """Campos base compartidos"""
    nombre: str = Field(..., min_length=3, max_length=100, description="Nombre del rol")
    descripcion: Optional[str] = Field(None, description="Descripción del rol")


# ============================================
# SCHEMA PARA CREAR ROL
# ============================================
class RolCreate(RolBase):
    """
    Datos necesarios para crear un rol.
    Solo Superadmin puede crear roles.
    """
    es_sistema: bool = Field(False, description="Si es un rol de sistema (no eliminable)")


# ============================================
# SCHEMA PARA ACTUALIZAR ROL
# ============================================
class RolUpdate(BaseModel):
    """Datos opcionales para actualizar un rol"""
    nombre: Optional[str] = Field(None, min_length=3, max_length=100)
    descripcion: Optional[str] = None


# ============================================
# SCHEMA DE RESPUESTA
# ============================================
class RolResponse(RolBase):
    """Datos que se devuelven al cliente"""
    id: int
    es_sistema: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# SCHEMA DETALLADO
# ============================================
class RolDetalle(RolResponse):
    """Información detallada del rol con estadísticas"""
    updated_at: datetime
    total_usuarios: Optional[int] = Field(0, description="Cantidad de usuarios con este rol")
    total_permisos: Optional[int] = Field(0, description="Cantidad de permisos asignados")
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# SCHEMA PARA ASIGNAR ROL A USUARIO
# ============================================
class AsignarRolUsuario(BaseModel):
    """Datos para asignar un rol a un usuario"""
    usuario_id: int = Field(..., gt=0, description="ID del usuario")
    rol_id: int = Field(..., gt=0, description="ID del rol")


# ============================================
# SCHEMA PARA ASIGNAR MÚLTIPLES ROLES
# ============================================
class AsignarRolesUsuario(BaseModel):
    """Datos para asignar múltiples roles a un usuario"""
    usuario_id: int = Field(..., gt=0, description="ID del usuario")
    roles_ids: List[int] = Field(..., min_items=1, description="Lista de IDs de roles")