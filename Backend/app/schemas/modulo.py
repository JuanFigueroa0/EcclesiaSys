from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


# ============================================
# SCHEMA BASE
# ============================================
class ModuloBase(BaseModel):
    """Campos base compartidos"""
    nombre: str = Field(..., min_length=3, max_length=150, description="Nombre del módulo")
    codigo: str = Field(..., min_length=2, max_length=100, description="Código único del módulo")
    descripcion: Optional[str] = Field(None, description="Descripción del módulo")


# ============================================
# SCHEMA PARA CREAR MÓDULO
# ============================================
class ModuloCreate(ModuloBase):
    """
    Datos necesarios para crear un módulo.
    """
    activo: bool = Field(True, description="Si el módulo está activo")


# ============================================
# SCHEMA PARA ACTUALIZAR MÓDULO
# ============================================
class ModuloUpdate(BaseModel):
    """Datos opcionales para actualizar un módulo"""
    nombre: Optional[str] = Field(None, min_length=3, max_length=150)
    codigo: Optional[str] = Field(None, min_length=2, max_length=100)
    descripcion: Optional[str] = None
    activo: Optional[bool] = None


# ============================================
# SCHEMA DE RESPUESTA
# ============================================
class ModuloResponse(ModuloBase):
    """Datos que se devuelven al cliente"""
    id: int
    activo: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# SCHEMA DETALLADO (con permisos asociados)
# ============================================
class ModuloDetalle(ModuloResponse):
    """Información detallada del módulo"""
    updated_at: datetime
    total_permisos: Optional[int] = Field(0, description="Cantidad de permisos asociados")
    
    model_config = ConfigDict(from_attributes=True)