# app/schemas/persona.py
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from datetime import date, datetime


class PersonaBase(BaseModel):
    primer_nombre:    str = Field(..., min_length=1, max_length=100)
    segundo_nombre:   Optional[str] = Field(None, max_length=100)
    primer_apellido:  str = Field(..., min_length=1, max_length=100)
    segundo_apellido: Optional[str] = Field(None, max_length=100)

    @field_validator('primer_nombre', 'primer_apellido')
    @classmethod
    def validar_nombres_obligatorios(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Este campo no puede estar vacío')
        return v.strip().title()

    @field_validator('segundo_nombre', 'segundo_apellido')
    @classmethod
    def validar_nombres_opcionales(cls, v: Optional[str]) -> Optional[str]:
        if v is None or not v.strip():
            return None
        return v.strip().title()


class PersonaCreate(PersonaBase):
    fecha_nacimiento: Optional[date] = None
    sexo:             Optional[str]  = Field(None, pattern="^(masculino|femenino)$")
    lugar_nacimiento: Optional[str]  = Field(None, max_length=255)
    region:           Optional[str]  = Field(None, max_length=100)
    departamento:     Optional[str]  = Field(None, max_length=100)
    municipio:        Optional[str]  = Field(None, max_length=100)
    tipo_documento:   str            = Field(..., pattern="^(CC|TI|CE|PA|RC|sin_documento)$")
    numero_documento: Optional[str]  = Field(None, max_length=100)
    estado_civil:     str            = Field("soltero", pattern="^(soltero|casado|viudo|divorciado|union_libre|religioso_casado|anulado)$")

    @field_validator('numero_documento')
    @classmethod
    def validar_documento(cls, v: Optional[str], info) -> Optional[str]:
        tipo_doc = info.data.get('tipo_documento')
        if tipo_doc == 'sin_documento':
            return None
        if not v or not v.strip():
            raise ValueError('Debes proporcionar el número de documento')
        return v.strip()

    @field_validator('region', 'departamento', 'municipio')
    @classmethod
    def validar_ubicacion(cls, v: Optional[str]) -> Optional[str]:
        if v is None or not v.strip():
            return None
        return v.strip().title()


class PersonaUpdate(BaseModel):
    primer_nombre:    Optional[str]  = Field(None, min_length=1, max_length=100)
    segundo_nombre:   Optional[str]  = Field(None, max_length=100)
    primer_apellido:  Optional[str]  = Field(None, min_length=1, max_length=100)
    segundo_apellido: Optional[str]  = Field(None, max_length=100)
    fecha_nacimiento: Optional[date] = None
    sexo:             Optional[str]  = Field(None, pattern="^(masculino|femenino)$")
    lugar_nacimiento: Optional[str]  = Field(None, max_length=255)
    region:           Optional[str]  = Field(None, max_length=100)
    departamento:     Optional[str]  = Field(None, max_length=100)
    municipio:        Optional[str]  = Field(None, max_length=100)
    tipo_documento:   Optional[str]  = Field(None, pattern="^(CC|TI|CE|PA|RC|sin_documento)$")
    numero_documento: Optional[str]  = Field(None, max_length=100)
    estado_civil:     Optional[str]  = Field(None, pattern="^(soltero|casado|viudo|divorciado|union_libre|religioso_casado|anulado)$")
    # ── Foto ──
    foto_url:         Optional[str]  = None
    foto_public_id:   Optional[str]  = None


class PersonaResponse(PersonaBase):
    id:               int
    fecha_nacimiento: Optional[date]     = None
    sexo:             Optional[str]      = None
    lugar_nacimiento: Optional[str]      = None
    region:           Optional[str]      = None
    departamento:     Optional[str]      = None
    municipio:        Optional[str]      = None
    tipo_documento:   str
    numero_documento: Optional[str]      = None
    estado_civil:     str
    tiene_usuario:    bool
    created_at:       datetime
    # ── Foto ──
    foto_url:         Optional[str]      = None
    foto_public_id:   Optional[str]      = None

    model_config = ConfigDict(from_attributes=True)