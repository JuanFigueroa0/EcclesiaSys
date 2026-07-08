from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Usuario(Base):
    """
    Modelo ORM para la tabla usuarios.
    Representa cuentas de acceso al sistema.
    """
    __tablename__ = "usuarios"
    
    id = Column(BigInteger, primary_key=True, index=True)
    correo = Column(String(255), unique=True, nullable=False, index=True)
    hash_contrasena = Column(Text, nullable=False)
    
    # Validación de correo
    correo_validado = Column(Boolean, default=False)
    token_validacion = Column(String(255), nullable=True)
    token_expiracion = Column(DateTime(timezone=True), nullable=True)
    
    # Estado
    perfil_completo = Column(Boolean, default=False)
    estado = Column(String(50), default='pendiente_validacion', nullable=False)
    eliminado_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relación con roles asignados
    usuario_roles = relationship("UsuarioRol", back_populates="usuario")
    
    # NUEVA: Relación con persona (perfil)
    persona_usuario = relationship("PersonaUsuario", back_populates="usuario", uselist=False)
    
    # Relación con permisos directos (sin rol)
    permisos_directos = relationship("UsuarioPermiso", back_populates="usuario", cascade="all, delete-orphan")

    # Relación con sesiones activas
    sesiones = relationship("SesionUsuario", back_populates="usuario", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Usuario(id={self.id}, correo='{self.correo}', estado='{self.estado}')>"