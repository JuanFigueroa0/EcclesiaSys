from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime

from app.models.auditoria import Auditoria


class AuditoriaRepository:
    """
    Repositorio para registrar eventos de auditoría.
    """
    
    @staticmethod
    def registrar(
        db: Session,
        accion: str,
        entidad: str,
        usuario_id: Optional[int] = None,
        entidad_id: Optional[int] = None,
        descripcion: Optional[str] = None,
        datos_anteriores: Optional[Dict[str, Any]] = None,
        datos_nuevos: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Auditoria:
        """
        Registra un evento de auditoría.
        
        Args:
            db: Sesión de base de datos
            accion: Acción realizada (crear, actualizar, eliminar, etc.)
            entidad: Entidad afectada (usuario, rol, permiso, etc.)
            usuario_id: ID del usuario que realizó la acción
            entidad_id: ID del registro afectado
            descripcion: Descripción detallada
            datos_anteriores: Estado anterior del registro (JSON)
            datos_nuevos: Estado nuevo del registro (JSON)
            ip_address: IP del cliente
            user_agent: User agent del cliente
            
        Returns:
            Registro de auditoría creado
        """
        registro = Auditoria(
            usuario_id=usuario_id,
            accion=accion,
            entidad=entidad,
            entidad_id=entidad_id,
            descripcion=descripcion,
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.add(registro)
        db.commit()
        db.refresh(registro)
        
        return registro
    
    @staticmethod
    def get_by_usuario(
        db: Session,
        usuario_id: int,
        limit: int = 100,
        skip: int = 0
    ):
        """Obtiene registros de auditoría de un usuario específico"""
        return db.query(Auditoria).filter(
            Auditoria.usuario_id == usuario_id
        ).order_by(Auditoria.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_entidad(
        db: Session,
        entidad: str,
        entidad_id: Optional[int] = None,
        limit: int = 100,
        skip: int = 0
    ):
        """Obtiene registros de auditoría de una entidad específica"""
        query = db.query(Auditoria).filter(Auditoria.entidad == entidad)
        
        if entidad_id:
            query = query.filter(Auditoria.entidad_id == entidad_id)
        
        return query.order_by(Auditoria.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_all(
        db: Session,
        limit: int = 100,
        skip: int = 0
    ):
        """Obtiene todos los registros de auditoría"""
        return db.query(Auditoria).order_by(
            Auditoria.created_at.desc()
        ).offset(skip).limit(limit).all()