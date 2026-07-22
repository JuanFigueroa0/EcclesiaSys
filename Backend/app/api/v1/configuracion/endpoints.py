from fastapi import APIRouter

router = APIRouter()

mock_config = {
    "nombre_parroquia": "Parroquia San José",
    "direccion": "Calle 72 #45-20, Barranquilla",
    "telefono": "605 356 7890",
    "email_parroquia": "info@sanjose.com",
    "parroco_actual": "Pbro. Luis Rodríguez",
    "plantilla_activa": "clasica",
    "incluir_qr": True,
    "incluir_sello": True,
    "dias_retencion_docs": 1825,
    "notif_email": True,
    "notif_telegram": False,
    "telegram_bot_token": "",
}

@router.get("/", summary="Obtener configuración parroquial")
def obtener_configuracion():
    return mock_config

@router.put("/", summary="Actualizar configuración")
def actualizar_configuracion(payload: dict):
    mock_config.update(payload)
    return mock_config
