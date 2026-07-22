from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.deps import get_db, get_current_user
from app.models.usuario import Usuario
from app.models.persona import Persona
from app.schemas.persona import PersonaResponse, PersonaCreate, PersonaUpdate
from app.repositories.persona import PersonaRepository

router = APIRouter()

@router.get("/", response_model=List[PersonaResponse], summary="Listar todas las personas")
def listar_personas(
    buscar: Optional[str] = Query(None, description="Buscar por nombre o documento"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    query = db.query(Persona)
    if buscar:
        term = f"%{buscar}%"
        query = query.filter(
            (Persona.primer_nombre.ilike(term)) |
            (Persona.primer_apellido.ilike(term)) |
            (Persona.numero_documento.ilike(term))
        )
    return query.order_by(Persona.id.desc()).all()

@router.get("/{persona_id}", response_model=PersonaResponse, summary="Obtener persona por ID")
def obtener_persona(
    persona_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    persona = PersonaRepository.get_by_id(db, persona_id)
    if not persona:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Persona no encontrada")
    return persona

@router.post("/", response_model=PersonaResponse, status_code=status.HTTP_201_CREATED, summary="Crear persona")
def crear_persona(
    payload: PersonaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return PersonaRepository.create(
        db=db,
        primer_nombre=payload.primer_nombre,
        segundo_nombre=payload.segundo_nombre,
        primer_apellido=payload.primer_apellido,
        segundo_apellido=payload.segundo_apellido,
        tipo_documento=payload.tipo_documento,
        numero_documento=payload.numero_documento,
        fecha_nacimiento=payload.fecha_nacimiento,
        sexo=payload.sexo,
        lugar_nacimiento=payload.lugar_nacimiento,
        region=payload.region,
        departamento=payload.departamento,
        municipio=payload.municipio,
        estado_civil=payload.estado_civil or 'soltero'
    )

@router.put("/{persona_id}", response_model=PersonaResponse, summary="Actualizar persona")
def actualizar_persona(
    persona_id: int,
    payload: PersonaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    persona = PersonaRepository.get_by_id(db, persona_id)
    if not persona:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Persona no encontrada")
    
    update_data = payload.dict(exclude_unset=True)
    return PersonaRepository.update(db, persona, **update_data)
