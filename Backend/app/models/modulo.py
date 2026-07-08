from sqlalchemy import Column, BigInteger, String, Boolean, Text, TIMESTAMP
from sqlalchemy.sql import func
from app.core.database import Base


class Modulo(Base):
    __tablename__ = "modulos"

    id = Column(BigInteger, primary_key=True, index=True)
    nombre = Column(String(150), unique=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, default=True)
    codigo = Column(String(100), unique=True, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Modulo(id={self.id}, nombre='{self.nombre}')>"