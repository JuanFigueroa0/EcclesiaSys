from sqlalchemy import Column, BigInteger, String, Boolean, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Rol(Base):
    __tablename__ = "roles"

    id = Column(BigInteger, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    es_sistema = Column(Boolean, default=False)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    usuario_roles = relationship("UsuarioRol", back_populates="rol")
    rol_permisos = relationship("RolPermiso", back_populates="rol", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Rol(id={self.id}, nombre='{self.nombre}')>"