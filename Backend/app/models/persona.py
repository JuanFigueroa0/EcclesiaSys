# app/models/persona.py
from sqlalchemy import Column, BigInteger, String, Date, DateTime, Text, CheckConstraint, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Persona(Base):
    __tablename__ = "personas"

    id = Column(BigInteger, primary_key=True, index=True)

    primer_nombre    = Column(String(100), nullable=False)
    segundo_nombre   = Column(String(100), nullable=True)
    primer_apellido  = Column(String(100), nullable=False)
    segundo_apellido = Column(String(100), nullable=True)

    fecha_nacimiento = Column(Date, nullable=True)
    sexo             = Column(String(20), nullable=True)
    lugar_nacimiento = Column(String(255), nullable=True)

    region       = Column(String(100), nullable=True)
    departamento = Column(String(100), nullable=True)
    municipio    = Column(String(100), nullable=True)

    tipo_documento   = Column(String(50), nullable=False)
    numero_documento = Column(String(100), nullable=True)

    estado_civil  = Column(String(50), nullable=False, default='soltero')
    tiene_usuario = Column(Boolean, default=False)
    observaciones = Column(Text, nullable=True)

    # ── Foto de perfil ─────────────────────────────────────
    foto_url       = Column(Text, nullable=True)   # URL segura de Cloudinary
    foto_public_id = Column(Text, nullable=True)   # Para reemplazar/eliminar
    # ───────────────────────────────────────────────────────

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    persona_usuario = relationship("PersonaUsuario", back_populates="persona", uselist=False)

    __table_args__ = (
        CheckConstraint(
            "(tipo_documento = 'sin_documento' AND numero_documento IS NULL) OR "
            "(tipo_documento != 'sin_documento' AND numero_documento IS NOT NULL)",
            name='check_documento'
        ),
    )

    def __repr__(self):
        return f"<Persona(id={self.id}, nombre='{self.primer_nombre} {self.primer_apellido}')>"