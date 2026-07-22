from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional

router = APIRouter()

mock_eventos = []

@router.get("/", summary="Listar eventos")
def listar_eventos():
    return mock_eventos

@router.post("/", status_code=status.HTTP_201_CREATED, summary="Crear evento")
def crear_evento(payload: dict):
    nuevo = {
        "id": len(mock_eventos) + 1,
        "titulo": payload.get("titulo", ""),
        "tipo": payload.get("tipo", "misa"),
        "estado": payload.get("estado", "publicado"),
        "fecha": payload.get("fecha", "2026-07-20"),
        "hora": payload.get("hora", "08:00"),
        "lugar": payload.get("lugar", "Templo Principal"),
        "cupo": int(payload.get("cupo", 50)),
        "inscritos": 0
    }
    mock_eventos.append(nuevo)
    return nuevo
