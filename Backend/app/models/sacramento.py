from sqlalchemy import (
    Column, BigInteger, String, Boolean, Text,
    Integer, Numeric, ForeignKey, TIMESTAMP
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Sacramento(Base):
    __tablename__ = "sacramentos"

    id = Column(BigInteger, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    genera_certificado = Column(Boolean, default=False)
    nivel_riesgo = Column(String(20), nullable=True)  # bajo | alto
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, default=True)
    requiere_pago = Column(Boolean, default=False)
    monto_sugerido = Column(Numeric(10, 2), nullable=True)
    edad_minima = Column(Integer, nullable=True)
    edad_maxima = Column(Integer, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    requisitos = relationship(
        "RequisitoSacramento",
        foreign_keys="RequisitoSacramento.sacramento_id",
        back_populates="sacramento",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Sacramento(id={self.id}, nombre='{self.nombre}')>"


class RequisitoSacramento(Base):
    __tablename__ = "requisitos_sacramento"

    id = Column(BigInteger, primary_key=True, index=True)
    sacramento_id = Column(
        BigInteger,
        ForeignKey("sacramentos.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    tipo_requisito = Column(String(100), nullable=False)
    # sacramento_previo | documento | curso | edad | estado_civil | otro
    descripcion = Column(Text, nullable=False)
    obligatorio = Column(Boolean, default=True)
    sacramento_previo_id = Column(
        BigInteger,
        ForeignKey("sacramentos.id", ondelete="SET NULL"),
        nullable=True
    )
    orden = Column(Integer, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    sacramento = relationship(
        "Sacramento",
        foreign_keys=[sacramento_id],
        back_populates="requisitos"
    )
    sacramento_previo = relationship(
        "Sacramento",
        foreign_keys=[sacramento_previo_id]
    )

    def __repr__(self):
        return f"<RequisitoSacramento(id={self.id}, tipo='{self.tipo_requisito}')>"