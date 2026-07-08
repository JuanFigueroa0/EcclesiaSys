from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import Optional
from app.models.solicitud import (
    SolicitudSacramento,
    SolicitudSacramentoPersona,
    DocumentoSolicitud,
    Validacion
)


class SolicitudRepository:

    # ──────────────────────────────────────────
    # SOLICITUD PRINCIPAL
    # ──────────────────────────────────────────

    @staticmethod
    def crear(db: Session, datos: dict) -> SolicitudSacramento:
        solicitud = SolicitudSacramento(**datos)
        db.add(solicitud)
        db.commit()
        db.refresh(solicitud)
        return solicitud

    @staticmethod
    def get_by_id(db: Session, solicitud_id: int) -> SolicitudSacramento | None:
        return (
            db.query(SolicitudSacramento)
            .options(
                joinedload(SolicitudSacramento.personas),
                joinedload(SolicitudSacramento.documentos),
                joinedload(SolicitudSacramento.validaciones),
            )
            .filter(SolicitudSacramento.id == solicitud_id)
            .first()
        )

    @staticmethod
    def listar_por_usuario(
        db: Session,
        usuario_id: int,
        pagina: int = 1,
        por_pagina: int = 10,
        estado: Optional[str] = None
    ) -> tuple[list[SolicitudSacramento], int]:
        query = db.query(SolicitudSacramento).filter(
            SolicitudSacramento.usuario_solicitante_id == usuario_id
        )
        if estado:
            query = query.filter(SolicitudSacramento.estado == estado)

        total = query.count()
        items = (
            query.order_by(desc(SolicitudSacramento.created_at))
            .offset((pagina - 1) * por_pagina)
            .limit(por_pagina)
            .all()
        )
        return items, total

    @staticmethod
    def listar_todas(
        db: Session,
        pagina: int = 1,
        por_pagina: int = 10,
        estado: Optional[str] = None,
        sacramento_id: Optional[int] = None
    ) -> tuple[list[SolicitudSacramento], int]:
        """Para secretario/párroco — ver todas las solicitudes."""
        query = db.query(SolicitudSacramento)

        if estado:
            query = query.filter(SolicitudSacramento.estado == estado)
        if sacramento_id:
            query = query.filter(SolicitudSacramento.sacramento_id == sacramento_id)

        total = query.count()
        items = (
            query.order_by(desc(SolicitudSacramento.created_at))
            .offset((pagina - 1) * por_pagina)
            .limit(por_pagina)
            .all()
        )
        return items, total

    @staticmethod
    def actualizar_estado(
        db: Session,
        solicitud: SolicitudSacramento,
        estado: str,
        observaciones_secretario: Optional[str] = None
    ) -> SolicitudSacramento:
        solicitud.estado = estado
        if observaciones_secretario is not None:
            solicitud.observaciones_secretario = observaciones_secretario
        db.commit()
        db.refresh(solicitud)
        return solicitud

    @staticmethod
    def actualizar(
        db: Session,
        solicitud: SolicitudSacramento,
        datos: dict
    ) -> SolicitudSacramento:
        for campo, valor in datos.items():
            setattr(solicitud, campo, valor)
        db.commit()
        db.refresh(solicitud)
        return solicitud

    # ──────────────────────────────────────────
    # PERSONAS EN SOLICITUD
    # ──────────────────────────────────────────

    @staticmethod
    def agregar_persona(
        db: Session,
        solicitud_id: int,
        persona_id: int,
        rol: str,
        datos_digitados: dict
    ) -> SolicitudSacramentoPersona:
        entrada = SolicitudSacramentoPersona(
            solicitud_sacramento_id=solicitud_id,
            persona_id=persona_id,
            rol_en_solicitud=rol,
            datos_digitados=datos_digitados
        )
        db.add(entrada)
        db.commit()
        db.refresh(entrada)
        return entrada

    @staticmethod
    def get_persona_en_solicitud(
        db: Session,
        solicitud_id: int,
        persona_id: int,
        rol: str
    ) -> SolicitudSacramentoPersona | None:
        return db.query(SolicitudSacramentoPersona).filter(
            SolicitudSacramentoPersona.solicitud_sacramento_id == solicitud_id,
            SolicitudSacramentoPersona.persona_id == persona_id,
            SolicitudSacramentoPersona.rol_en_solicitud == rol
        ).first()

    @staticmethod
    def validar_persona(
        db: Session,
        entrada: SolicitudSacramentoPersona,
        datos_validados: bool,
        validado_por: int,
        observaciones: Optional[str] = None
    ) -> SolicitudSacramentoPersona:
        from datetime import datetime, timezone
        entrada.datos_validados = datos_validados
        entrada.validado_por = validado_por
        entrada.fecha_validacion = datetime.now(timezone.utc)
        entrada.observaciones_validacion = observaciones
        db.commit()
        db.refresh(entrada)
        return entrada

    # ──────────────────────────────────────────
    # DOCUMENTOS EN SOLICITUD
    # ──────────────────────────────────────────

    @staticmethod
    def agregar_documento(
        db: Session,
        solicitud_id: int,
        archivo_id: int,
        tipo_documento: str,
        persona_id: Optional[int] = None,
        descripcion: Optional[str] = None,
        es_reutilizado: bool = False
    ) -> DocumentoSolicitud:
        doc = DocumentoSolicitud(
            solicitud_sacramento_id=solicitud_id,
            archivo_id=archivo_id,
            tipo_documento=tipo_documento,
            persona_id=persona_id,
            descripcion=descripcion,
            es_reutilizado=es_reutilizado
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    @staticmethod
    def listar_documentos(
        db: Session,
        solicitud_id: int
    ) -> list[DocumentoSolicitud]:
        return db.query(DocumentoSolicitud).filter(
            DocumentoSolicitud.solicitud_sacramento_id == solicitud_id
        ).all()

    # ──────────────────────────────────────────
    # VALIDACIONES (secretario/párroco)
    # ──────────────────────────────────────────

    @staticmethod
    def crear_validacion(
        db: Session,
        solicitud_id: int,
        revisor_id: int,
        resultado: str,
        comentarios: Optional[str] = None,
        documentos_faltantes: Optional[str] = None
    ) -> Validacion:
        validacion = Validacion(
            solicitud_sacramento_id=solicitud_id,
            usuario_revisor_id=revisor_id,
            resultado=resultado,
            comentarios=comentarios,
            documentos_faltantes=documentos_faltantes
        )
        db.add(validacion)
        db.commit()
        db.refresh(validacion)
        return validacion

    @staticmethod
    def listar_validaciones(
        db: Session,
        solicitud_id: int
    ) -> list[Validacion]:
        return db.query(Validacion).filter(
            Validacion.solicitud_sacramento_id == solicitud_id
        ).order_by(desc(Validacion.created_at))  .all()