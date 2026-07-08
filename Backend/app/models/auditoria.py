from sqlalchemy import Column, BigInteger, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.core.database import Base


class Auditoria(Base):
    __tablename__ = "auditoria"

    id = Column(BigInteger, primary_key=True, index=True)
    usuario_id = Column(BigInteger, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True)
    accion = Column(String(100), nullable=False)
    entidad = Column(String(100), nullable=False)
    entidad_id = Column(BigInteger, nullable=True)
    descripcion = Column(Text, nullable=True)
    datos_anteriores = Column(JSONB, nullable=True)
    datos_nuevos = Column(JSONB, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<Auditoria(id={self.id}, accion='{self.accion}', entidad='{self.entidad}')>"