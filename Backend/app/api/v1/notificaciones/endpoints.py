from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_user
from app.models.usuario import Usuario

router = APIRouter()

# Almacén temporal de notificaciones generadas en tiempo de ejecución
notificaciones_db: List[dict] = []

@router.get("/", summary="Listar notificaciones del usuario")
def listar_notificaciones(
    current_user: Usuario = Depends(get_current_user)
):
    # Filtrar notificaciones para el usuario o sistema
    user_notifs = [n for n in notificaciones_db if n.get("usuario_id") == current_user.id or n.get("global")]
    return user_notifs

@router.put("/{notificacion_id}/marcar-leida", summary="Marcar notificacion como leída")
def marcar_leida(
    notificacion_id: int,
    current_user: Usuario = Depends(get_current_user)
):
    for n in notificaciones_db:
        if n["id"] == notificacion_id:
            n["leida"] = True
            return n
    return {"mensaje": "Ok"}

@router.put("/marcar-todas-leidas", summary="Marcar todas como leídas")
def marcar_todas_leidas(
    current_user: Usuario = Depends(get_current_user)
):
    for n in notificaciones_db:
        if n.get("usuario_id") == current_user.id or n.get("global"):
            n["leida"] = True
    return {"mensaje": "Todas leídas"}
