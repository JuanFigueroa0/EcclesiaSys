from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.models.persona import Persona


class PersonaRepository:
    """
    Repositorio para operaciones CRUD de personas.
    """
    
    @staticmethod
    def create(
        db: Session,
        primer_nombre: str,
        primer_apellido: str,
        tipo_documento: str,
        segundo_nombre: Optional[str] = None,
        segundo_apellido: Optional[str] = None,
        fecha_nacimiento: Optional[date] = None,
        sexo: Optional[str] = None,
        lugar_nacimiento: Optional[str] = None,
        region: Optional[str] = None,  
        departamento: Optional[str] = None,  
        municipio: Optional[str] = None,  
        numero_documento: Optional[str] = None,
        estado_civil: str = 'soltero',
        tiene_usuario: bool = False
    ) -> Persona:
        """Crea una nueva persona"""
        persona = Persona(
            primer_nombre=primer_nombre,
            segundo_nombre=segundo_nombre,
            primer_apellido=primer_apellido,
            segundo_apellido=segundo_apellido,
            fecha_nacimiento=fecha_nacimiento,
            sexo=sexo,
            lugar_nacimiento=lugar_nacimiento,
            region=region,  
            departamento=departamento,  
            municipio=municipio,  
            tipo_documento=tipo_documento,
            numero_documento=numero_documento,
            estado_civil=estado_civil,
            tiene_usuario=tiene_usuario
        )
        db.add(persona)
        db.commit()
        db.refresh(persona)
        return persona
    
    @staticmethod
    def get_by_id(db: Session, persona_id: int) -> Optional[Persona]:
        """Busca una persona por ID"""
        return db.query(Persona).filter(Persona.id == persona_id).first()
    
    @staticmethod
    def get_by_documento(db: Session, tipo_documento: str, numero_documento: str) -> Optional[Persona]:
        """Busca una persona por documento"""
        return db.query(Persona).filter(
            Persona.tipo_documento == tipo_documento,
            Persona.numero_documento == numero_documento
        ).first()
    
    @staticmethod
    def get_by_usuario_id(db: Session, usuario_id: int) -> Optional[Persona]:
        """Obtiene la persona asociada a un usuario"""
        from app.models.persona_usuario import PersonaUsuario
        
        vinculo = db.query(PersonaUsuario).filter(
            PersonaUsuario.usuario_id == usuario_id
        ).first()
        
        if vinculo:
            return db.query(Persona).filter(Persona.id == vinculo.persona_id).first()
        
        return None
    
    @staticmethod
    def update(db: Session, persona: Persona, **kwargs) -> Persona:
        """Actualiza campos de una persona"""
        for key, value in kwargs.items():
            if hasattr(persona, key) and value is not None:
                setattr(persona, key, value)
        
        db.commit()
        db.refresh(persona)
        return persona