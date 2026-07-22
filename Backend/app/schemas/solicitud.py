from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any
from datetime import date, time, datetime
from enum import Enum


# ─────────────────────────────────────────────
# ENUMS
# ─────────────────────────────────────────────

class EstadoSolicitud(str, Enum):
    pendiente = "pendiente"
    en_revision = "en_revision"
    documentacion_incompleta = "documentacion_incompleta"
    aprobada = "aprobada"
    rechazada = "rechazada"
    cancelada = "cancelada"


class RolEnSolicitud(str, Enum):
    receptor = "receptor"
    padre = "padre"
    madre = "madre"
    padrino = "padrino"
    madrina = "madrina"
    contrayente = "contrayente"
    testigo = "testigo"
    tutor_legal = "tutor_legal"
    solicitante = "solicitante"
    otro = "otro"


class ResultadoValidacion(str, Enum):
    aprobado = "aprobado"
    rechazado = "rechazado"
    requiere_correccion = "requiere_correccion"
    documentacion_incompleta = "documentacion_incompleta"


# ─────────────────────────────────────────────
# PERSONA EN SOLICITUD
# ─────────────────────────────────────────────

class DatosDigitadosPersona(BaseModel):
    """
    Datos que el usuario digita en texto para cada persona involucrada.
    Sirven para que el secretario los compare con el documento subido.
    """
    primer_nombre: str = Field(..., min_length=1, max_length=100)
    segundo_nombre: Optional[str] = Field(None, max_length=100)
    primer_apellido: str = Field(..., min_length=1, max_length=100)
    segundo_apellido: Optional[str] = Field(None, max_length=100)
    tipo_documento: str = Field(..., description="CC | TI | CE | PA | RC | sin_documento")
    numero_documento: Optional[str] = Field(None, max_length=100)
    fecha_nacimiento: Optional[date] = None
    lugar_nacimiento: Optional[str] = Field(None, max_length=255)

    @field_validator("tipo_documento")
    @classmethod
    def validar_tipo_documento(cls, v):
        permitidos = ["CC", "TI", "CE", "PA", "RC", "sin_documento"]
        if v not in permitidos:
            raise ValueError(f"tipo_documento debe ser uno de: {', '.join(permitidos)}")
        return v


class SolicitudPersonaCreate(BaseModel):
    """Persona que se añade a una solicitud."""
    persona_id: Optional[int] = Field(
        None,
        description="ID si la persona ya existe en el sistema. "
                    "Si no existe, se crea con datos_digitados."
    )
    rol_en_solicitud: RolEnSolicitud
    datos_digitados: DatosDigitadosPersona = Field(
        ...,
        description="Datos en texto para validación del secretario"
    )


class SolicitudPersonaOut(BaseModel):
    id: int
    persona_id: int
    rol_en_solicitud: str
    datos_digitados: Optional[Any] = None
    datos_validados: bool
    validado_por: Optional[int] = None
    fecha_validacion: Optional[datetime] = None
    observaciones_validacion: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ValidarPersonaSolicitudRequest(BaseModel):
    """Secretario valida los datos de una persona en la solicitud."""
    datos_validados: bool
    observaciones_validacion: Optional[str] = None


# ─────────────────────────────────────────────
# DOCUMENTO EN SOLICITUD
# ─────────────────────────────────────────────

class DocumentoSolicitudOut(BaseModel):
    id: int
    persona_id: Optional[int] = None
    archivo_id: int
    tipo_documento: str
    descripcion: Optional[str] = None
    es_reutilizado: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# VALIDACIÓN (secretario/párroco)
# ─────────────────────────────────────────────

class ValidacionCreate(BaseModel):
    """Secretario o párroco registra una validación sobre la solicitud."""
    resultado: ResultadoValidacion
    comentarios: Optional[str] = None
    documentos_faltantes: Optional[str] = Field(
        None,
        description="Lista de documentos faltantes separados por coma"
    )


class ValidacionOut(BaseModel):
    id: int
    solicitud_sacramento_id: int
    usuario_revisor_id: int
    resultado: str
    comentarios: Optional[str] = None
    documentos_faltantes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# SOLICITUD SACRAMENTO — CREAR
# ─────────────────────────────────────────────

class SolicitudSacramentoCreate(BaseModel):
    """
    Payload principal para crear una solicitud de sacramento.
    El usuario envía: sacramento, fecha preferida, personas involucradas.
    Los documentos se suben en endpoints separados (multipart/form-data).
    """
    sacramento_id: int = Field(..., description="ID del sacramento solicitado")
    fecha_preferida: Optional[date] = None
    hora_preferida: Optional[time] = None
    motivo: Optional[str] = Field(None, max_length=1000)
    observaciones: Optional[str] = Field(None, max_length=2000)

    # Personas involucradas (receptor, padres, padrinos, etc.)
    personas: List[SolicitudPersonaCreate] = Field(
        ...,
        min_length=1,
        description="Mínimo debe incluir al receptor del sacramento"
    )

    @field_validator("personas")
    @classmethod
    def validar_tiene_receptor(cls, v):
        """
        Matrimonio usa 'contrayente' como rol principal.
        Otros sacramentos usan 'receptor'.
        Al menos uno de estos roles debe estar presente.
        """
        ROLES_PRINCIPALES = {
            RolEnSolicitud.receptor,
            RolEnSolicitud.contrayente,
        }
        roles_presentes = {p.rol_en_solicitud for p in v}
        if not roles_presentes.intersection(ROLES_PRINCIPALES):
            raise ValueError(
                "Debe incluir al menos una persona con rol 'receptor' o 'contrayente'"
            )
        return v


class SolicitudSacramentoUpdate(BaseModel):
    """Actualización parcial — usuario puede editar mientras está en 'pendiente'."""
    fecha_preferida: Optional[date] = None
    hora_preferida: Optional[time] = None
    motivo: Optional[str] = Field(None, max_length=1000)
    observaciones: Optional[str] = Field(None, max_length=2000)


class CambiarEstadoSolicitud(BaseModel):
    """Secretario cambia el estado de una solicitud."""
    estado: EstadoSolicitud
    observaciones_secretario: Optional[str] = Field(
        None,
        max_length=2000,
        description="Observaciones del secretario (obligatorio si rechazada o documentacion_incompleta)"
    )

    @field_validator("observaciones_secretario")
    @classmethod
    def observaciones_requeridas_en_rechazo(cls, v, info):
        estado = info.data.get("estado")
        if estado in [EstadoSolicitud.rechazada, EstadoSolicitud.documentacion_incompleta]:
            if not v or not v.strip():
                raise ValueError(
                    "Las observaciones son obligatorias cuando el estado es "
                    "'rechazada' o 'documentacion_incompleta'"
                )
        return v


# ─────────────────────────────────────────────
# SOLICITUD SACRAMENTO — RESPUESTAS
# ─────────────────────────────────────────────

class SolicitudSacramentoOut(BaseModel):
    """Respuesta completa de una solicitud."""
    id: int
    usuario_solicitante_id: int
    sacramento_id: int
    estado: str
    motivo: Optional[str] = None
    observaciones: Optional[str] = None
    observaciones_secretario: Optional[str] = None
    requiere_validacion_manual: bool
    fecha_preferida: Optional[date] = None
    hora_preferida: Optional[time] = None
    created_at: datetime
    updated_at: datetime

    # Detalle de personas y documentos
    personas: List[SolicitudPersonaOut] = []
    documentos: List[DocumentoSolicitudOut] = []
    validaciones: List[ValidacionOut] = []

    class Config:
        from_attributes = True


class SolicitudSacramentoListItem(BaseModel):
    """Versión reducida para listar solicitudes (tabla/listado)."""
    id: int
    sacramento_id: int
    sacramento_nombre: Optional[str] = None
    usuario_correo: Optional[str] = None
    persona_nombre: Optional[str] = None
    estado: str
    requiere_validacion_manual: bool
    fecha_preferida: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedSolicitudes(BaseModel):
    """Respuesta paginada para listado de solicitudes."""
    total: int
    pagina: int
    por_pagina: int
    items: List[SolicitudSacramentoListItem]