# app/services/cloudinary_service.py
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, HTTPException, status
from app.core.cloudinary_config import init_cloudinary

init_cloudinary()

# ── Categorías válidas ──────────────────────────────────────
CATEGORIAS_VALIDAS = [
    "documento_identidad",
    "certificado_externo",
    "registro_civil",
    "acta_defuncion",
    "documento_anulacion",
    "custodia_legal",
    "certificado_curso",
    "certificado_sacramento",
    "foto_persona",
    "foto_perfil",
    "otro"
]

# ── Solo imágenes para estas categorías ────────────────────
CATEGORIAS_SOLO_IMAGEN = {"foto_perfil", "foto_persona"}

# ── Extensiones permitidas por tipo ────────────────────────
EXTENSIONES_PERMITIDAS = {
    "imagen":    ["jpg", "jpeg", "png", "webp"],
    "pdf":       ["pdf"],
    "documento": ["pdf", "jpg", "jpeg", "png"]
}

# ── Límites de tamaño por categoría ────────────────────────
LIMITES_CATEGORIA = {
    "foto_perfil":  2 * 1024 * 1024,   # 2 MB
    "foto_persona": 2 * 1024 * 1024,   # 2 MB
    "default":     10 * 1024 * 1024,   # 10 MB (documentos)
}

# ── Transformaciones Cloudinary por categoría ───────────────
TRANSFORMACIONES = {
    "foto_perfil": {
        "transformation": [
            {"width": 400, "height": 400, "crop": "fill", "gravity": "face"},
            {"quality": "auto:good"},
            {"fetch_format": "auto"},
        ]
    },
    "foto_persona": {
        "transformation": [
            {"width": 400, "height": 400, "crop": "fill", "gravity": "face"},
            {"quality": "auto:good"},
            {"fetch_format": "auto"},
        ]
    },
    "documento_identidad": {
        "transformation": [
            {"width": 1200, "quality": "auto:good"},
            {"fetch_format": "auto"},
        ]
    },
}


def _detectar_tipo_archivo(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext in ["jpg", "jpeg", "png", "webp"]:
        return "imagen"
    elif ext == "pdf":
        return "pdf"
    return "documento"


def _validar_extension(filename: str, tipo_archivo: str) -> None:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    permitidas = EXTENSIONES_PERMITIDAS.get(tipo_archivo, [])
    if ext not in permitidas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Extensión '.{ext}' no permitida. "
                f"Permitidas: {', '.join(permitidas)}"
            )
        )


def generar_public_id_foto_perfil(usuario_id: int) -> str:
    """
    Public_id fijo por usuario.
    ecclesiastica/usuarios/{id}/perfil/foto
    Cloudinary sobreescribe automáticamente con overwrite=True.
    """
    return f"ecclesiastica/usuarios/{usuario_id}/perfil/foto"



def generar_public_id_documento(
    usuario_id: int,
    categoria: str,
    nombre_archivo: str
) -> str:
    """
    Public_id para documentos de un usuario.
    ecclesiastica/usuarios/{id}/documentos/{categoria}/{nombre}
    """
    import re
    # Limpiar nombre para que sea válido como public_id
    nombre_limpio = re.sub(r'[^a-zA-Z0-9_\-]', '_', nombre_archivo)
    return f"ecclesiastica/usuarios/{usuario_id}/documentos/{categoria}/{nombre_limpio}"

async def subir_archivo(
    file: UploadFile,
    categoria: str,
    carpeta: str = "ecclesiastica",
    descripcion: str = None,
    public_id_personalizado: str = None,
) -> dict:
    """
    Sube un archivo a Cloudinary.
    Retorna dict con los datos para guardar en la tabla 'archivos'.
    """
    if categoria not in CATEGORIAS_VALIDAS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Categoría '{categoria}' no válida."
        )

    contenido = await file.read()
    tamanio   = len(contenido)

    if tamanio == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo está vacío."
        )

    limite = LIMITES_CATEGORIA.get(categoria, LIMITES_CATEGORIA["default"])
    if tamanio > limite:
        mb = limite // (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Archivo demasiado grande. Máximo para '{categoria}': {mb} MB."
        )

    nombre_original = file.filename or "sin_nombre"
    tipo_archivo    = _detectar_tipo_archivo(nombre_original)

    if categoria in CATEGORIAS_SOLO_IMAGEN and tipo_archivo != "imagen":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La categoría '{categoria}' solo acepta imágenes (jpg, jpeg, png, webp)."
        )

    _validar_extension(nombre_original, tipo_archivo)

    ext = nombre_original.rsplit(".", 1)[-1].lower() if "." in nombre_original else ""

    opciones = {
        "folder":        f"{carpeta}/{categoria}",
        # "auto" permite que Cloudinary detecte correctamente imágenes Y PDFs.
        # Usar "raw" para PDFs los sube sin tipo reconocido (aparece como N/A
        # en el dashboard) y bloquea transformaciones y visualización inline.
        "resource_type": "auto",
    }

    # Transformaciones automáticas según categoría
    if categoria in TRANSFORMACIONES:
        opciones.update(TRANSFORMACIONES[categoria])

    # Public_id fijo → sobreescribe imagen anterior (para fotos de perfil)
    if public_id_personalizado:
        opciones["public_id"]  = public_id_personalizado
        opciones["overwrite"]  = True
        opciones["invalidate"] = True   # invalida caché CDN
        opciones.pop("folder", None)    # no usar folder si public_id ya tiene path

    try:
        import io
        resultado = cloudinary.uploader.upload(io.BytesIO(contenido), **opciones)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir a Cloudinary: {str(e)}"
        )

    return {
        "cloudinary_public_id": resultado["public_id"],
        "cloudinary_url":       resultado["secure_url"],
        "tipo_archivo":         tipo_archivo,
        "categoria":            categoria,
        "nombre_original":      nombre_original,
        "tamanio_bytes":        tamanio,
        "descripcion":          descripcion,
    }


async def eliminar_archivo(public_id: str, resource_type: str = "image") -> bool:
    """Elimina un archivo de Cloudinary."""
    try:
        resultado = cloudinary.uploader.destroy(
            public_id, resource_type=resource_type
        )
        return resultado.get("result") == "ok"
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar de Cloudinary: {str(e)}"
        )


def generar_url_transformada(public_id: str, **transformaciones) -> str:
    """Genera URL con transformaciones (útil para thumbnails)."""
    return cloudinary.CloudinaryImage(public_id).build_url(**transformaciones)