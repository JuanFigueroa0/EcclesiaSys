from sqlalchemy import Column, BigInteger, String, Boolean, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class SesionUsuario(Base):
    __tablename__ = "sesiones_usuario"

    id = Column(BigInteger, primary_key=True, index=True)
    usuario_id = Column(BigInteger, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)

    session_token = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token = Column(Text, unique=True, nullable=False, index=True)

    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    dispositivo = Column(String(100), nullable=True)
    ubicacion = Column(String(255), nullable=True)

    fecha_creacion = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    fecha_ultimo_uso = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    fecha_expiracion = Column(TIMESTAMP(timezone=True), nullable=False)

    activa = Column(Boolean, default=True, nullable=False)
    revocada = Column(Boolean, default=False, nullable=False)
    motivo_revocacion = Column(String(255), nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relación
    usuario = relationship("Usuario", back_populates="sesiones")