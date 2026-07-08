from sqlalchemy import Column, BigInteger, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class PersonaUsuario(Base):
    __tablename__ = "persona_usuario"

    id = Column(BigInteger, primary_key=True, index=True)
    persona_id = Column(BigInteger, ForeignKey("personas.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    usuario_id = Column(BigInteger, ForeignKey("usuarios.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    fecha_vinculacion = Column(TIMESTAMP(timezone=True), server_default=func.now())

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    persona = relationship("Persona", back_populates="persona_usuario")
    usuario = relationship("Usuario", back_populates="persona_usuario")

    def __repr__(self):
        return f"<PersonaUsuario(persona_id={self.persona_id}, usuario_id={self.usuario_id})>"
