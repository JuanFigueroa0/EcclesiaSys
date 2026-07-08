from sqlalchemy.orm import Session
from typing import Optional

from app.models.persona_usuario import PersonaUsuario


class PersonaUsuarioRepository:
    """
    Repositorio para vincular personas con usuarios.
    """
    
    @staticmethod
    def create(db: Session, persona_id: int, usuario_id: int) -> PersonaUsuario:
        """Vincula una persona con un usuario"""
        vinculo = PersonaUsuario(
            persona_id=persona_id,
            usuario_id=usuario_id
        )
        db.add(vinculo)
        db.commit()
        db.refresh(vinculo)
        return vinculo
    
    @staticmethod
    def get_by_usuario_id(db: Session, usuario_id: int) -> Optional[PersonaUsuario]:
        """Obtiene el vínculo por usuario_id"""
        return db.query(PersonaUsuario).filter(
            PersonaUsuario.usuario_id == usuario_id
        ).first()
    
    @staticmethod
    def get_by_persona_id(db: Session, persona_id: int) -> Optional[PersonaUsuario]:
        """Obtiene el vínculo por persona_id"""
        return db.query(PersonaUsuario).filter(
            PersonaUsuario.persona_id == persona_id
        ).first()