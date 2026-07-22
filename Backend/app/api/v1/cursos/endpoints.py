from fastapi import APIRouter, status

router = APIRouter()

mock_cursos = [
    {
        "id": 1,
        "nombre": "Catequesis de Confirmación 2026",
        "sacramento": "Confirmación",
        "catequista": "Hermana María Elena",
        "fecha_inicio": "2026-03-01",
        "fecha_fin": "2026-11-30",
        "estado": "en_curso",
        "inscritos": 35,
    },
    {
        "id": 2,
        "nombre": "Pre-Bautismal Niños y Padrinos",
        "sacramento": "Bautismo",
        "catequista": "Diácono Roberto",
        "fecha_inicio": "2026-07-01",
        "fecha_fin": "2026-07-15",
        "estado": "abierto",
        "inscritos": 14,
    },
]

@router.get("/", summary="Listar cursos de catequesis")
def listar_cursos():
    return mock_cursos

@router.post("/", status_code=status.HTTP_201_CREATED, summary="Aperturar curso")
def crear_curso(payload: dict):
    nuevo = {
        "id": len(mock_cursos) + 1,
        "nombre": payload.get("nombre", ""),
        "sacramento": payload.get("sacramento", "Bautismo"),
        "catequista": payload.get("catequista", "Por asignar"),
        "fecha_inicio": payload.get("fecha_inicio", "2026-07-20"),
        "fecha_fin": payload.get("fecha_fin", "2026-12-01"),
        "estado": "abierto",
        "inscritos": 0
    }
    mock_cursos.append(nuevo)
    return nuevo
