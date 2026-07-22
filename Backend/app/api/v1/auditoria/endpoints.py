from fastapi import APIRouter

router = APIRouter()

mock_logs = [
    {
        "id": 1,
        "usuario": "admin@ecclesiasys.com",
        "accion": "EMISION_CERTIFICADO",
        "modulo": "Certificados",
        "detalle": "Emisión de Certificado Bautismal #CERT-2026-001",
        "ip": "192.168.1.10",
        "fecha": "2026-06-15 10:45:12",
    },
    {
        "id": 2,
        "usuario": "secretaria@ecclesiasys.com",
        "accion": "CREAR",
        "modulo": "Personas",
        "detalle": "Creación de registro para persona: Juan García Martínez",
        "ip": "192.168.1.15",
        "fecha": "2026-06-15 09:12:00",
    },
]

@router.get("/", summary="Obtener bitácora de auditoría")
def obtener_auditoria():
    return mock_logs
