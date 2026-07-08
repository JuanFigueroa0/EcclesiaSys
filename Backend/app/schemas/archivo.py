from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ArchivoBase(BaseModel):
    tipo_archivo: str = Field(..., description="imagen | pdf | documento")
    categoria: Optional[str] = Field(None, description="documento_identidad | registro_civil | etc.")
    nombre_original: Optional[str] = None
    tamanio_bytes: Optional[int] = None
    descripcion: Optional[str] = None


class ArchivoCreate(ArchivoBase):
    cloudinary_public_id: str
    cloudinary_url: str


class ArchivoOut(ArchivoBase):
    id: int
    cloudinary_public_id: str
    cloudinary_url: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ArchivoSimple(BaseModel):
    """Schema reducido para embeber en otras respuestas."""
    id: int
    cloudinary_url: str
    tipo_archivo: str
    categoria: Optional[str] = None
    nombre_original: Optional[str] = None

    class Config:
        from_attributes = True