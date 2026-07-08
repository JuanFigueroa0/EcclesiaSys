from sqlalchemy import Column, BigInteger, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class RolPermiso(Base):
    __tablename__ = "rol_permiso"

    id = Column(BigInteger, primary_key=True, index=True)
    rol_id = Column(BigInteger, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)
    permiso_id = Column(BigInteger, ForeignKey("permisos.id", ondelete="CASCADE"), nullable=False, index=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("rol_id", "permiso_id", name="unique_rol_permiso"),
    )

    # Relaciones
    rol = relationship("Rol", back_populates="rol_permisos")
    permiso = relationship("Permiso")

    def __repr__(self):
        return f"<RolPermiso(rol_id={self.rol_id}, permiso_id={self.permiso_id})>"