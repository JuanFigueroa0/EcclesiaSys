# app/api/v1/archivos/endpoints.py
import logging
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.repositories.archivo import ArchivoRepository
from app.api.deps import get_db, get_current_active_user
from app.models.usuario import Usuario
from app.models.persona_usuario import PersonaUsuario
from app.services.cloudinary_service import (
    subir_archivo,
    eliminar_archivo,
    generar_public_id_foto_perfil,
)

router = APIRouter()
logger = logging.getLogger(__name__)


def _obtener_persona_del_usuario(db: Session, usuario_id: int):
    """Helper: obtiene la persona vinculada al usuario o lanza 400."""
    vinculo = (
        db.query(PersonaUsuario)
        .filter(PersonaUsuario.usuario_id == usuario_id)
        .first()
    )
    if not vinculo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Completa tu perfil antes de subir una foto.",
        )
    return vinculo.persona


@router.post(
    "/foto-perfil",
    summary="Subir o reemplazar foto de perfil",
    description=(
        "Sube la foto de perfil del usuario. "
        "Si ya tiene una, la reemplaza automáticamente — "
        "solo existe una foto de perfil por usuario."
    ),
)
async def subir_foto_perfil(
    file: UploadFile = File(..., description="Imagen jpg/jpeg/png/webp · máx 2 MB"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    persona   = _obtener_persona_del_usuario(db, current_user.id)
    public_id = generar_public_id_foto_perfil(current_user.id)
    #
    # public_id fijo + overwrite=True en cloudinary_service garantiza
    # que solo existe UNA foto de perfil. No hay que eliminar la anterior
    # manualmente — Cloudinary la reemplaza en el mismo public_id.
    #
    resultado = await subir_archivo(
        file=file,
        categoria="foto_perfil",
        public_id_personalizado=public_id,
        descripcion=f"Foto de perfil usuario {current_user.id}",
    )

    # Actualizar BD
    persona.foto_url       = resultado["cloudinary_url"]
    persona.foto_public_id = resultado["cloudinary_public_id"]
    db.commit()
    db.refresh(persona)

    return {
        "ok":      True,
        "foto_url": persona.foto_url,
        "mensaje": "Foto de perfil actualizada correctamente.",
    }


@router.delete(
    "/foto-perfil",
    summary="Eliminar foto de perfil",
)
async def eliminar_foto_perfil(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    persona = _obtener_persona_del_usuario(db, current_user.id)

    if not persona.foto_public_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tienes foto de perfil para eliminar.",
        )

    public_id_a_eliminar = persona.foto_public_id

    # ── Paso 1: limpiar BD primero ──────────────────────────
    # Si Cloudinary falla después, la BD queda limpia y el usuario
    # puede volver a subir sin problemas. La imagen huérfana en
    # Cloudinary es menos grave que una URL rota en BD.
    persona.foto_url       = None
    persona.foto_public_id = None
    db.commit()

    # ── Paso 2: eliminar de Cloudinary ─────────────────────
    try:
        await eliminar_archivo(public_id_a_eliminar, resource_type="image")
    except Exception as e:
        # Log pero no fallar — la BD ya está limpia
        logger.warning(
            f"No se pudo eliminar {public_id_a_eliminar} de Cloudinary: {e}"
        )

    return {"ok": True, "mensaje": "Foto de perfil eliminada."}


@router.post(
    "/documento",
    summary="Subir documento",
    description="Sube un documento (PDF o imagen) para sacramentos u otros usos.",
)
async def subir_documento(
    file:         UploadFile    = File(...),
    categoria:    str           = Form(...),
    descripcion:  Optional[str] = Form(None),
    db:           Session       = Depends(get_db),
    current_user: Usuario       = Depends(get_current_active_user),
):
    resultado = await subir_archivo(
        file=file,
        categoria=categoria,
        descripcion=descripcion,
    )
    return {
        "ok":                   True,
        "cloudinary_url":       resultado["cloudinary_url"],
        "cloudinary_public_id": resultado["cloudinary_public_id"],
        "tipo_archivo":         resultado["tipo_archivo"],
        "categoria":            resultado["categoria"],
        "nombre_original":      resultado["nombre_original"],
        "tamanio_bytes":        resultado["tamanio_bytes"],
    }


@router.get(
    "/{archivo_id}/visor",
    summary="Obtener URL de visualización del archivo",
    description=(
        "Devuelve la URL optimizada para visualizar el archivo en el navegador. "
        "Para PDFs genera una URL de Cloudinary con fl_attachment:false. "
        "Para imágenes genera una URL con transformación de calidad automática."
    ),
)
async def obtener_url_visor(
    archivo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    archivo = ArchivoRepository.get_by_id(db, archivo_id)

    if not archivo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo no encontrado.",
        )

    url_visor = archivo.cloudinary_url
    tipo = archivo.tipo_archivo  # "pdf" | "imagen" | "documento"

    # Cloudinary con resource_type="auto" convierte PDFs a imagen y les asigna
    # extension .jpg en la URL. Si la URL ya tiene extension de imagen, el tipo
    # real para el visor es "imagen" aunque en BD figure como "pdf".
    # Esto evita que el frontend intente renderizarlo con un visor PDF cuando
    # en realidad es un JPG normal.
    EXTENSIONES_IMAGEN = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    url_sin_params = url_visor.split("?")[0].lower()
    extension_url  = ("." + url_sin_params.rsplit(".", 1)[-1]) if "." in url_sin_params else ""
    url_es_imagen  = extension_url in EXTENSIONES_IMAGEN

    if tipo == "pdf" and url_es_imagen:
        # PDF convertido a imagen por Cloudinary -> mostrar como imagen
        tipo = "imagen"
        if "/upload/" in url_visor and "q_auto" not in url_visor:
            url_visor = url_visor.replace("/upload/", "/upload/q_auto,f_auto/")

    elif tipo == "pdf":
        # PDF real (sin conversion a imagen): forzar visualizacion inline
        if "/upload/" in url_visor and "fl_inline" not in url_visor:
            url_visor = url_visor.replace("/upload/", "/upload/fl_inline/")

    elif tipo == "imagen":
        if "/upload/" in url_visor and "q_auto" not in url_visor:
            url_visor = url_visor.replace("/upload/", "/upload/q_auto,f_auto/")

    return {
        "ok": True,
        "archivo_id": archivo.id,
        "url_visor": url_visor,
        # tipo_archivo refleja como debe renderizarse (puede diferir del valor en BD)
        "tipo_archivo": tipo,
        "nombre_original": archivo.nombre_original,
        "categoria": archivo.categoria,
    }