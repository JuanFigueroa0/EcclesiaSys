from fastapi import APIRouter, status

router = APIRouter()

mock_certificados = []

@router.get("/", summary="Listar certificados")
def listar_certificados():
    return mock_certificados

@router.post("/", status_code=status.HTTP_201_CREATED, summary="Generar certificado")
def generar_certificado(payload: dict):
    nuevo = {
        "id": len(mock_certificados) + 1,
        "codigo": f"CERT-2026-00{len(mock_certificados) + 1}",
        "tipo": payload.get("tipo", "bautismo"),
        "persona_nombre": payload.get("persona_nombre", ""),
        "fecha_emision": "2026-07-20",
        "solicitante": payload.get("solicitante", payload.get("persona_nombre", "Self")),
        "estado": "emitido"
    }
    mock_certificados.append(nuevo)
    return nuevo
