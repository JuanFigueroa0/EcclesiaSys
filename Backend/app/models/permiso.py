from sqlalchemy import Column, BigInteger, String, Boolean, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Permiso(Base):
    __tablename__ = "permisos"

    id = Column(BigInteger, primary_key=True, index=True)
    codigo = Column(String(100), unique=True, nullable=False, index=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)
    modulo_id = Column(BigInteger, ForeignKey("modulos.id", ondelete="CASCADE"), nullable=True, index=True)
    activo = Column(Boolean, default=True, nullable=False)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relaciones
    modulo = relationship("Modulo")

    def __repr__(self):
        return f"<Permiso(id={self.id}, codigo='{self.codigo}')>"