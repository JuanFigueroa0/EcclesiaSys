# app/services/solicitud_service.py
import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from typing import Optional

from app.models.solicitud import SolicitudSacramento
from app.models.sacramento import Sacramento
from app.repositories.solicitud import SolicitudRepository
from app.repositories.persona import PersonaRepository
from app.repositories.archivo import ArchivoRepository
from app.services.cloudinary_service import subir_archivo

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# HELPERS INTERNOS
# ─────────────────────────────────────────────

def _get_sacramento_o_404(db: Session, sacramento_id: int) -> Sacramento:
    sacramento = db.query(Sacramento).filter(
        Sacramento.id == sacramento_id,
        Sacramento.activo == True
    ).first()
    if not sacramento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sacramento con ID {sacramento_id} no existe o está inactivo"
        )
    return sacramento


def _get_solicitud_o_404(db: Session, solicitud_id: int) -> SolicitudSacramento:
    solicitud = SolicitudRepository.get_by_id(db, solicitud_id)
    if not solicitud:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Solicitud con ID {solicitud_id} no encontrada"
        )
    return solicitud


def _verificar_propietario_o_admin(
    solicitud: SolicitudSacramento,
    usuario_id: int,
    es_admin: bool = False
) -> None:
    if not es_admin and solicitud.usuario_solicitante_id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a esta solicitud"
        )


def _solicitud_editable(solicitud: SolicitudSacramento) -> None:
    estados_editables = ["pendiente", "documentacion_incompleta"]
    if solicitud.estado not in estados_editables:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"La solicitud en estado '{solicitud.estado}' no puede ser modificada. "
                f"Solo se pueden editar solicitudes en: {', '.join(estados_editables)}"
            )
        )


def _buscar_o_crear_persona(db: Session, datos_digitados: dict) -> tuple[int, bool]:
    """
    Busca una persona por documento. Si existe la retorna.
    Si no existe, la crea con los datos digitados.

    Returns:
        (persona_id, es_nueva) — es_nueva=True si se creó en este momento
    """
    tipo_doc = datos_digitados.get("tipo_documento")
    num_doc  = datos_digitados.get("numero_documento")

    if tipo_doc and num_doc and tipo_doc != "sin_documento":
        persona_existente = PersonaRepository.get_by_documento(db, tipo_doc, num_doc)
        if persona_existente:
            return persona_existente.id, False

    nueva_persona = PersonaRepository.create(
        db=db,
        primer_nombre    = datos_digitados["primer_nombre"],
        segundo_nombre   = datos_digitados.get("segundo_nombre"),
        primer_apellido  = datos_digitados["primer_apellido"],
        segundo_apellido = datos_digitados.get("segundo_apellido"),
        tipo_documento   = tipo_doc or "sin_documento",
        numero_documento = num_doc,
        fecha_nacimiento = datos_digitados.get("fecha_nacimiento"),
        lugar_nacimiento = datos_digitados.get("lugar_nacimiento"),
        tiene_usuario    = False
    )
    return nueva_persona.id, True


def _verificar_documentos_existentes(
    db: Session,
    persona_id: int,
    tipos_requeridos: list[str]
) -> dict:
    """
    Verifica qué documentos de una persona ya existen en documentos_persona.
    Retorna dict: { tipo_documento: archivo_id | None }

    Solo considera documentos vigentes y validados.
    Los no validados se tratan como inexistentes (el secretario aún no los ha aprobado).
    """
    from app.models.solicitud import DocumentoSolicitud
    from app.models.archivo import Archivo

    # Buscar en documentos_persona (documentos permanentes, validados por secretario)
    try:
        from app.models.solicitud import DocumentoSolicitud as DS
        # Importar el modelo correcto de documentos_persona
        from sqlalchemy import text
        resultado = db.execute(
            text("""
                SELECT dp.tipo_documento_archivo, dp.archivo_id
                FROM documentos_persona dp
                WHERE dp.persona_id = :persona_id
                  AND dp.vigente = true
                  AND dp.validado = true
                  AND dp.tipo_documento_archivo = ANY(:tipos)
            """),
            {"persona_id": persona_id, "tipos": tipos_requeridos}
        ).fetchall()

        encontrados = {row[0]: row[1] for row in resultado}
    except Exception as e:
        logger.warning(f"Error verificando documentos: {e}")
        encontrados = {}

    return {
        tipo: encontrados.get(tipo)
        for tipo in tipos_requeridos
    }


# ─────────────────────────────────────────────
# CREAR SOLICITUD
# ─────────────────────────────────────────────

def crear_solicitud(
    db: Session,
    usuario_id: int,
    sacramento_id: int,
    personas_data: list,
    fecha_preferida=None,
    hora_preferida=None,
    motivo: Optional[str] = None,
    observaciones: Optional[str] = None
) -> SolicitudSacramento:
    """
    Crea solicitud de sacramento.

    Flujo:
      1. Validar sacramento activo
      2. Crear registro de solicitud
      3. Por cada persona: buscar en BD o crear nueva
      4. Vincular personas con su rol y datos digitados
      5. Verificar documentos existentes en documentos_persona
      6. Los documentos encontrados se vinculan como reutilizados
      7. El sistema NO expone qué documentos encontró al usuario —
         solo le informa cuáles faltan para que los suba.
    """
    # 1. Validar sacramento
    sacramento = _get_sacramento_o_404(db, sacramento_id)

    # 2. Crear solicitud
    requiere_manual = sacramento.nivel_riesgo == "alto"
    solicitud = SolicitudRepository.crear(db, {
        "usuario_solicitante_id": usuario_id,
        "sacramento_id":          sacramento_id,
        "estado":                 "pendiente",
        "requiere_validacion_manual": requiere_manual,
        "fecha_preferida":        fecha_preferida,
        "hora_preferida":         hora_preferida,
        "motivo":                 motivo,
        "observaciones":          observaciones,
    })

    # 3, 4 y 5. Procesar personas
    for p in personas_data:
        # Soportar tanto objeto Pydantic como dict plano
        dd = p.datos_digitados
        raw = dd.model_dump() if hasattr(dd, "model_dump") else dict(dd)
        datos = _serializar_datos(raw)
        persona_id, es_nueva = _buscar_o_crear_persona(db, datos)

        SolicitudRepository.agregar_persona(
            db              = db,
            solicitud_id    = solicitud.id,
            persona_id      = persona_id,
            rol             = p.rol_en_solicitud.value if hasattr(p.rol_en_solicitud, "value") else p.rol_en_solicitud,
            datos_digitados = datos
        )

        if not es_nueva:
            tipos_doc_solicitud = [
                "documento_identidad",
                "registro_civil",
                "certificado_bautismo",
                "certificado_confirmacion",
                "certificado_primera_comunion",
                "certificado_matrimonio",
                "acta_defuncion",
                "certificado_curso",
            ]
            docs_existentes = _verificar_documentos_existentes(
                db, persona_id, tipos_doc_solicitud
            )

            for tipo_doc, archivo_id in docs_existentes.items():
                if archivo_id is not None:
                    SolicitudRepository.agregar_documento(
                        db             = db,
                        solicitud_id   = solicitud.id,
                        archivo_id     = archivo_id,
                        tipo_documento = tipo_doc,
                        persona_id     = persona_id,
                        descripcion    = "Documento existente vinculado automáticamente",
                        es_reutilizado = True
                    )

    # Recargar con todas las relaciones
    return SolicitudRepository.get_by_id(db, solicitud.id)


# ─────────────────────────────────────────────
# LISTAR SOLICITUDES
# ─────────────────────────────────────────────

def _format_solicitud_list_item(s: SolicitudSacramento) -> dict:
    sacramento_nom = s.sacramento.nombre if hasattr(s, 'sacramento') and s.sacramento else f"Sacramento #{s.sacramento_id}"
    usuario_email = s.usuario_solicitante.correo if hasattr(s, 'usuario_solicitante') and s.usuario_solicitante else None

    persona_nom = None
    if hasattr(s, 'personas') and s.personas:
        for p in s.personas:
            if hasattr(p, 'datos_digitados') and p.datos_digitados and isinstance(p.datos_digitados, dict):
                pn = p.datos_digitados.get('primer_nombre') or p.datos_digitados.get('nombres') or ''
                pa = p.datos_digitados.get('primer_apellido') or p.datos_digitados.get('apellidos') or ''
                if pn or pa:
                    persona_nom = f"{pn} {pa}".strip()
                    break
            if not persona_nom and hasattr(p, 'persona') and p.persona:
                persona_nom = f"{p.persona.nombres} {p.persona.apellidos}".strip()
                break

    if not persona_nom and hasattr(s, 'usuario_solicitante') and s.usuario_solicitante and hasattr(s.usuario_solicitante, 'persona') and s.usuario_solicitante.persona:
        persona_nom = f"{s.usuario_solicitante.persona.nombres} {s.usuario_solicitante.persona.apellidos}".strip()

    if not persona_nom:
        persona_nom = usuario_email or f"Solicitud #{s.id}"

    return {
        "id": s.id,
        "sacramento_id": s.sacramento_id,
        "sacramento_nombre": sacramento_nom,
        "usuario_correo": usuario_email,
        "persona_nombre": persona_nom,
        "estado": s.estado,
        "requiere_validacion_manual": s.requiere_validacion_manual,
        "fecha_preferida": s.fecha_preferida,
        "created_at": s.created_at,
        "updated_at": s.updated_at
    }


def listar_mis_solicitudes(
    db: Session,
    usuario_id: int,
    pagina: int = 1,
    por_pagina: int = 10,
    estado: Optional[str] = None
) -> dict:
    items, total = SolicitudRepository.listar_por_usuario(
        db, usuario_id, pagina, por_pagina, estado
    )
    return {
        "total":     total,
        "pagina":    pagina,
        "por_pagina": por_pagina,
        "items":     [_format_solicitud_list_item(s) for s in items]
    }


def listar_todas_solicitudes(
    db: Session,
    pagina: int = 1,
    por_pagina: int = 10,
    estado: Optional[str] = None,
    sacramento_id: Optional[int] = None
) -> dict:
    items, total = SolicitudRepository.listar_todas(
        db, pagina, por_pagina, estado, sacramento_id
    )
    return {
        "total":     total,
        "pagina":    pagina,
        "por_pagina": por_pagina,
        "items":     [_format_solicitud_list_item(s) for s in items]
    }


# ─────────────────────────────────────────────
# OBTENER DETALLE
# ─────────────────────────────────────────────

def obtener_solicitud(
    db: Session,
    solicitud_id: int,
    usuario_id: int,
    es_admin: bool = False
) -> SolicitudSacramento:
    solicitud = _get_solicitud_o_404(db, solicitud_id)
    _verificar_propietario_o_admin(solicitud, usuario_id, es_admin)
    return solicitud


# ─────────────────────────────────────────────
# ACTUALIZAR (usuario)
# ─────────────────────────────────────────────

def actualizar_solicitud(
    db: Session,
    solicitud_id: int,
    usuario_id: int,
    datos: dict
) -> SolicitudSacramento:
    solicitud = _get_solicitud_o_404(db, solicitud_id)
    _verificar_propietario_o_admin(solicitud, usuario_id)
    _solicitud_editable(solicitud)

    campos_permitidos = {"fecha_preferida", "hora_preferida", "motivo", "observaciones"}
    datos_filtrados   = {k: v for k, v in datos.items() if k in campos_permitidos and v is not None}

    return SolicitudRepository.actualizar(db, solicitud, datos_filtrados)


# ─────────────────────────────────────────────
# CANCELAR (usuario)
# ─────────────────────────────────────────────

def cancelar_solicitud(
    db: Session,
    solicitud_id: int,
    usuario_id: int
) -> SolicitudSacramento:
    solicitud = _get_solicitud_o_404(db, solicitud_id)
    _verificar_propietario_o_admin(solicitud, usuario_id)

    estados_cancelables = ["pendiente", "documentacion_incompleta"]
    if solicitud.estado not in estados_cancelables:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede cancelar una solicitud en estado '{solicitud.estado}'"
        )

    return SolicitudRepository.actualizar_estado(db, solicitud, "cancelada")


# ─────────────────────────────────────────────
# SUBIR DOCUMENTO
# ─────────────────────────────────────────────

async def subir_documento_solicitud(
    db: Session,
    solicitud_id: int,
    usuario_id: int,
    file: UploadFile,
    tipo_documento: str,
    categoria: str,
    persona_id: Optional[int] = None,
    descripcion: Optional[str] = None,
    es_admin: bool = False
) -> dict:
    """
    Sube un documento a Cloudinary y lo vincula a la solicitud.

    Lógica de reutilización:
    - Busca en documentos_persona (documentos permanentes vigentes y validados).
    - Si existe un documento vigente+validado del mismo tipo para esa persona,
      lo reutiliza directamente sin subir nada nuevo.
    - Si no existe, sube el archivo y lo vincula.
    - El usuario NUNCA ve el contenido del documento existente —
      solo el secretario puede ver y comparar.
    """
    solicitud = _get_solicitud_o_404(db, solicitud_id)
    _verificar_propietario_o_admin(solicitud, usuario_id, es_admin)
    _solicitud_editable(solicitud)

    # ── Verificar reutilización desde documentos_persona ──
    if persona_id:
        try:
            from sqlalchemy import text
            row = db.execute(
                text("""
                    SELECT dp.archivo_id
                    FROM documentos_persona dp
                    WHERE dp.persona_id    = :persona_id
                      AND dp.tipo_documento_archivo = :tipo_doc
                      AND dp.vigente       = true
                      AND dp.validado      = true
                    LIMIT 1
                """),
                {"persona_id": persona_id, "tipo_doc": tipo_documento}
            ).fetchone()

            if row:
                # Reutilizar — no subir nada nuevo
                SolicitudRepository.agregar_documento(
                    db             = db,
                    solicitud_id   = solicitud_id,
                    archivo_id     = row[0],
                    tipo_documento = tipo_documento,
                    persona_id     = persona_id,
                    descripcion    = "Documento existente reutilizado",
                    es_reutilizado = True
                )
                return {
                    "mensaje":        "Se encontró y reutilizó un documento existente para esta persona.",
                    "es_reutilizado": True,
                    "archivo_id":     row[0]
                }
        except Exception as e:
            logger.warning(f"Error al verificar reutilización: {e}")

    # ── Subir nuevo archivo ────────────────────────────────
    # Path organizado: ecclesiastica/usuarios/{usuario_id}/documentos/{tipo}
    datos_cloudinary = await subir_archivo(
        file        = file,
        categoria   = categoria,
        carpeta     = f"ecclesiastica/usuarios/{usuario_id}/documentos",
        descripcion = descripcion
    )

    # Guardar en tabla archivos
    archivo = ArchivoRepository.crear(db, datos_cloudinary)

    # Vincular a la solicitud
    SolicitudRepository.agregar_documento(
        db             = db,
        solicitud_id   = solicitud_id,
        archivo_id     = archivo.id,
        tipo_documento = tipo_documento,
        persona_id     = persona_id,
        descripcion    = descripcion,
        es_reutilizado = False
    )

    return {
        "mensaje":        "Documento subido correctamente",
        "es_reutilizado": False,
        "archivo_id":     archivo.id,
        "url":            datos_cloudinary["cloudinary_url"]
    }


# ─────────────────────────────────────────────
# CAMBIAR ESTADO (secretario/párroco)
# ─────────────────────────────────────────────

def cambiar_estado_solicitud(
    db: Session,
    solicitud_id: int,
    nuevo_estado: str,
    revisor_id: int,
    observaciones_secretario: Optional[str] = None
) -> SolicitudSacramento:
    """
    Secretario cambia el estado con transiciones válidas.
    Registra entrada en validaciones para los estados definitivos.
    """
    solicitud = _get_solicitud_o_404(db, solicitud_id)

    transiciones = {
        "pendiente":                ["en_revision", "aprobada", "rechazada", "documentacion_incompleta", "cancelada"],
        "en_revision":              ["aprobada", "rechazada", "documentacion_incompleta", "pendiente", "cancelada"],
        "documentacion_incompleta": ["en_revision", "aprobada", "rechazada", "pendiente", "cancelada"],
        "aprobada":                 ["en_revision", "rechazada", "pendiente"],
        "rechazada":                ["en_revision", "aprobada", "pendiente"],
        "cancelada":                ["pendiente", "en_revision", "aprobada"],
    }

    permitidos = transiciones.get(solicitud.estado, [])
    if nuevo_estado not in permitidos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"No se puede pasar de '{solicitud.estado}' a '{nuevo_estado}'. "
                f"Transiciones permitidas: {', '.join(permitidos) or 'ninguna'}"
            )
        )

    # Registrar validación para estados con resultado definitivo
    estados_con_validacion = ["aprobada", "rechazada", "documentacion_incompleta"]
    if nuevo_estado in estados_con_validacion:
        resultado_map = {
            "aprobada":               "aprobado",
            "rechazada":              "rechazado",
            "documentacion_incompleta": "documentacion_incompleta"
        }
        SolicitudRepository.crear_validacion(
            db                  = db,
            solicitud_id        = solicitud_id,
            revisor_id          = revisor_id,
            resultado           = resultado_map[nuevo_estado],
            comentarios         = observaciones_secretario
        )

    return SolicitudRepository.actualizar_estado(
        db, solicitud, nuevo_estado, observaciones_secretario
    )

def _serializar_datos(datos: dict) -> dict:
    """
    Convierte tipos no serializables a JSON (date → str ISO).
    Necesario porque datos_digitados se guarda como JSONB.
    """
    resultado = {}
    for k, v in datos.items():
        if hasattr(v, "isoformat"):   # date, datetime, time
            resultado[k] = v.isoformat()
        else:
            resultado[k] = v
    return resultado
# ─────────────────────────────────────────────
# VALIDAR PERSONA EN SOLICITUD (secretario)
# ─────────────────────────────────────────────

def validar_persona_en_solicitud(
    db: Session,
    solicitud_id: int,
    persona_id: int,
    rol: str,
    datos_validados: bool,
    revisor_id: int,
    observaciones: Optional[str] = None
) -> dict:
    """
    Secretario confirma o rechaza que los datos digitados
    coinciden con el documento físico.
    """
    _get_solicitud_o_404(db, solicitud_id)

    entrada = SolicitudRepository.get_persona_en_solicitud(
        db, solicitud_id, persona_id, rol
    )
    if not entrada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró persona con ID {persona_id} y rol '{rol}' en esta solicitud"
        )

    resultado = SolicitudRepository.validar_persona(
        db              = db,
        entrada         = entrada,
        datos_validados = datos_validados,
        validado_por    = revisor_id,
        observaciones   = observaciones
    )

    return {
        "mensaje":         "Datos validados" if datos_validados else "Datos marcados como incorrectos",
        "persona_id":      persona_id,
        "datos_validados": resultado.datos_validados
    }