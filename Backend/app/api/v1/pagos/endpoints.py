from fastapi import APIRouter, status

router = APIRouter()

mock_pagos = [
    {
        "id": 1,
        "referencia": "PAGO-2026-089",
        "concepto": "Estipendio Certificado Bautismo",
        "monto": 25000,
        "fiel_nombre": "Juan García Martínez",
        "fecha": "2026-06-15",
        "metodo": "efectivo",
        "estado": "completado",
    },
    {
        "id": 2,
        "referencia": "PAGO-2026-090",
        "concepto": "Derechos Celebración Matrimonial",
        "monto": 150000,
        "fiel_nombre": "Carlos Pérez Soto",
        "fecha": "2026-06-14",
        "metodo": "transferencia",
        "estado": "completado",
    },
]

@router.get("/", summary="Listar recibos y pagos")
def listar_pagos():
    return mock_pagos

@router.post("/", status_code=status.HTTP_201_CREATED, summary="Registrar pago")
def registrar_pago(payload: dict):
    nuevo = {
        "id": len(mock_pagos) + 1,
        "referencia": f"PAGO-2026-09{len(mock_pagos) + 1}",
        "concepto": payload.get("concepto", "Estipendio Parroquial"),
        "monto": float(payload.get("monto", 0)),
        "fiel_nombre": payload.get("fiel_nombre", ""),
        "fecha": "2026-07-20",
        "metodo": payload.get("metodo", "efectivo"),
        "estado": "completado"
    }
    mock_pagos.append(nuevo)
    return nuevo
