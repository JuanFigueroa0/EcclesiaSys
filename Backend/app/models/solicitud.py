from sqlalchemy import (
    Column, BigInteger, String, Boolean, Text,
    Date, Time, ForeignKey, JSON, TIMESTAMP, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class SolicitudSacramento(Base):
    __tablename__ = "solicitudes_sacramento"

    id = Column(BigInteger, primary_key=True, index=True)
    usuario_solicitante_id = Column(
        BigInteger,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    sacramento_id = Column(
        BigInteger,
        ForeignKey("sacramentos.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    estado = Column(String(50), default="pendiente", nullable=False, index=True)
    motivo = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)
    observaciones_secretario = Column(Text, nullable=True)
    requiere_validacion_manual = Column(Boolean, default=True)
    fecha_preferida = Column(Date, nullable=True)
    hora_preferida = Column(Time, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    usuario_solicitante = relationship("Usuario", foreign_keys=[usuario_solicitante_id])
    sacramento = relationship("Sacramento")
    personas = relationship(
        "SolicitudSacramentoPersona",
        back_populates="solicitud",
        cascade="all, delete-orphan"
    )
    documentos = relationship(
        "DocumentoSolicitud",
        back_populates="solicitud",
        cascade="all, delete-orphan"
    )
    validaciones = relationship(
        "Validacion",
        back_populates="solicitud",
        cascade="all, delete-orphan"
    )


class SolicitudSacramentoPersona(Base):
    __tablename__ = "solicitud_sacramento_persona"

    id = Column(BigInteger, primary_key=True, index=True)
    solicitud_sacramento_id = Column(
        BigInteger,
        ForeignKey("solicitudes_sacramento.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    persona_id = Column(
        BigInteger,
        ForeignKey("personas.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    rol_en_solicitud = Column(String(100), nullable=False)

    # Datos digitados por el usuario en texto (para validación del secretario)
    datos_digitados = Column(JSON, nullable=True)

    # Validación
    datos_validados = Column(Boolean, default=False)
    validado_por = Column(BigInteger, nullable=True)  # Sin FK en BD real
    fecha_validacion = Column(TIMESTAMP(timezone=True), nullable=True)
    observaciones_validacion = Column(Text, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint(
            "solicitud_sacramento_id", "persona_id", "rol_en_solicitud",
            name="solicitud_sacramento_persona_solicitud_sacramento_id_person_key"
        ),
    )

    # Relaciones
    solicitud = relationship("SolicitudSacramento", back_populates="personas")
    persona = relationship("Persona")


class DocumentoSolicitud(Base):
    __tablename__ = "documentos_solicitud"

    id = Column(BigInteger, primary_key=True, index=True)
    solicitud_sacramento_id = Column(
        BigInteger,
        ForeignKey("solicitudes_sacramento.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    persona_id = Column(
        BigInteger,
        ForeignKey("personas.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    archivo_id = Column(
        BigInteger,
        ForeignKey("archivos.id", ondelete="RESTRICT"),
        nullable=False
    )

    tipo_documento = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    es_reutilizado = Column(Boolean, default=False)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    solicitud = relationship("SolicitudSacramento", back_populates="documentos")
    persona = relationship("Persona")
    archivo = relationship("Archivo")


class Validacion(Base):
    __tablename__ = "validaciones"

    id = Column(BigInteger, primary_key=True, index=True)
    solicitud_sacramento_id = Column(
        BigInteger,
        ForeignKey("solicitudes_sacramento.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    usuario_revisor_id = Column(
        BigInteger,
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=False,
        index=True
    )

    resultado = Column(String(50), nullable=False)
    comentarios = Column(Text, nullable=True)
    documentos_faltantes = Column(Text, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    solicitud = relationship("SolicitudSacramento", back_populates="validaciones")
    revisor = relationship("Usuario", foreign_keys=[usuario_revisor_id])