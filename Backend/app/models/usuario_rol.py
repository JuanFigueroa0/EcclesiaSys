from sqlalchemy import Column, BigInteger, Boolean, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class UsuarioRol(Base):
    __tablename__ = "usuario_rol"

    id = Column(BigInteger, primary_key=True, index=True)
    usuario_id = Column(BigInteger, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    rol_id = Column(BigInteger, ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False, index=True)
    activo = Column(Boolean, default=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("usuario_id", "rol_id", name="usuario_rol_usuario_id_rol_id_key"),
    )

    # Relaciones
    usuario = relationship("Usuario", back_populates="usuario_roles")
    rol = relationship("Rol", back_populates="usuario_roles")

    def __repr__(self):
        return f"<UsuarioRol(usuario_id={self.usuario_id}, rol_id={self.rol_id})>"