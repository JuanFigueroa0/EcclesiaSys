# app/models/usuario_permiso.py
from sqlalchemy import Column, BigInteger, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class UsuarioPermiso(Base):
    __tablename__ = "usuario_permiso"

    id         = Column(BigInteger, primary_key=True, index=True)
    usuario_id = Column(BigInteger, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    permiso_id = Column(BigInteger, ForeignKey("permisos.id", ondelete="CASCADE"), nullable=False, index=True)
    activo     = Column(Boolean, default=True, nullable=False)   # ← columna que faltaba

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relaciones
    usuario = relationship("Usuario", back_populates="permisos_directos")
    permiso = relationship("Permiso")

    def __repr__(self):
        return f"<UsuarioPermiso(usuario_id={self.usuario_id}, permiso_id={self.permiso_id}, activo={self.activo})>"