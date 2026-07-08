# app/api/v1/sacramentos/endpoints.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.sacramento import Sacramento, RequisitoSacramento

router = APIRouter()


@router.get(
    "/",
    summary="Listar sacramentos"
)
def listar_sacramentos(
    solo_activos: bool = Query(True, description="Solo sacramentos activos"),
    db: Session = Depends(get_db),
):
    query = db.query(Sacramento)
    if solo_activos:
        query = query.filter(Sacramento.activo == True)
    return query.order_by(Sacramento.id).all()


@router.get(
    "/{sacramento_id}",
    summary="Obtener sacramento por ID"
)
def obtener_sacramento(
    sacramento_id: int,
    db: Session = Depends(get_db),
):
    sacramento = db.query(Sacramento).filter(
        Sacramento.id == sacramento_id
    ).first()

    if not sacramento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sacramento no encontrado"
        )
    return sacramento


@router.get(
    "/{sacramento_id}/requisitos",
    summary="Obtener requisitos de un sacramento"
)
def obtener_requisitos_sacramento(
    sacramento_id: int,
    db: Session = Depends(get_db),
):
    sacramento = db.query(Sacramento).filter(
        Sacramento.id == sacramento_id,
        Sacramento.activo == True
    ).first()

    if not sacramento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sacramento no encontrado"
        )

    requisitos = (
        db.query(RequisitoSacramento)
        .filter(RequisitoSacramento.sacramento_id == sacramento_id)
        .order_by(RequisitoSacramento.orden)
        .all()
    )

    return [
        {
            "id":                   r.id,
            "tipo_requisito":       r.tipo_requisito,
            "descripcion":          r.descripcion,
            "obligatorio":          r.obligatorio,
            "sacramento_previo_id": r.sacramento_previo_id,
            "orden":                r.orden,
        }
        for r in requisitos
    ]