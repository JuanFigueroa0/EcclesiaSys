from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class CambioCorreoPendiente(Base):
    __tablename__ = "cambios_correo_pendientes"
    
    id = Column(BigInteger, primary_key=True, index=True)
    usuario_id = Column(BigInteger, ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Correos
    correo_anterior = Column(String(255), nullable=False)
    correo_nuevo = Column(String(255), nullable=False)
    
    # Token de validación
    token_validacion = Column(String(255), unique=True, nullable=False, index=True)
    token_expiracion = Column(DateTime(timezone=True), nullable=False)
    
    # Estado
    estado = Column(String(50), default='pendiente', nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relación
    usuario = relationship("Usuario")
    
    def __repr__(self):
        return f"<CambioCorreoPendiente(id={self.id}, usuario_id={self.usuario_id}, estado='{self.estado}')>"