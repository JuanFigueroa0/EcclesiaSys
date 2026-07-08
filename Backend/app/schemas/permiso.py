from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# ============================================
# SCHEMA BASE
# ============================================
class PermisoBase(BaseModel):
    """Campos base compartidos"""
    codigo: str = Field(..., min_length=3, max_length=100, description="Código único (ej: usuarios.listar)")
    nombre: str = Field(..., min_length=3, max_length=150, description="Nombre descriptivo")
    descripcion: Optional[str] = Field(None, description="Descripción detallada del permiso")


# ============================================
# SCHEMA PARA CREAR PERMISO
# ============================================
class PermisoCreate(PermisoBase):
    """
    Datos necesarios para crear un permiso.
    """
    modulo_id: Optional[int] = Field(None, description="ID del módulo asociado")


# ============================================
# SCHEMA PARA ACTUALIZAR PERMISO
# ============================================
class PermisoUpdate(BaseModel):
    """Datos opcionales para actualizar un permiso"""
    nombre: Optional[str] = Field(None, min_length=3, max_length=150)
    descripcion: Optional[str] = None
    activo: Optional[bool] = None


# ============================================
# SCHEMA DE RESPUESTA
# ============================================
class PermisoResponse(PermisoBase):
    """Datos que se devuelven al cliente"""
    id: int
    modulo_id: Optional[int] = None
    activo: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# SCHEMA DETALLADO
# ============================================
class PermisoDetalle(PermisoResponse):
    """Información detallada del permiso"""
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# SCHEMA PARA ASIGNAR PERMISOS A ROL
# ============================================
class AsignarPermisosRol(BaseModel):
    """Lista de permisos a asignar a un rol"""
    permisos_ids: List[int] = Field(..., min_items=1, description="Lista de IDs de permisos")


# ============================================
# SCHEMA PARA MIS PERMISOS
# ============================================
class MisPermisosResponse(BaseModel):
    """Respuesta con permisos del usuario actual"""
    usuario_id: int
    correo: str
    permisos: List[str] = Field(..., description="Lista de códigos de permisos")
    total: int = Field(..., description="Total de permisos")

# ============================================
# SCHEMAS PARA PERMISOS DIRECTOS DE USUARIO
# ============================================

class AsignarPermisosUsuario(BaseModel):
    """Lista de permisos a asignar directamente a un usuario"""
    permisos_ids: List[int] = Field(
        ..., description="Lista de IDs de permisos a asignar"
    )


class PermisoUsuarioResponse(BaseModel):
    """Permiso directo asignado a un usuario"""
    id:         int
    permiso_id: int
    activo:     bool
    permiso:    PermisoResponse

    model_config = ConfigDict(from_attributes=True)