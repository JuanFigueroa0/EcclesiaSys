from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional
from datetime import datetime, timezone

from app.models.cambio_correo import CambioCorreoPendiente


class CambioCorreoRepository:
    """Repository para gestionar cambios de correo pendientes."""
    
    @staticmethod
    def crear_cambio_pendiente(
        db: Session,
        usuario_id: int,
        correo_anterior: str,
        correo_nuevo: str,
        token_validacion: str,
        token_expiracion: datetime
    ) -> CambioCorreoPendiente:
        """Crea un nuevo cambio de correo pendiente."""
        cambio = CambioCorreoPendiente(
            usuario_id=usuario_id,
            correo_anterior=correo_anterior,
            correo_nuevo=correo_nuevo,
            token_validacion=token_validacion,
            token_expiracion=token_expiracion,
            estado='pendiente'
        )
        db.add(cambio)
        db.commit()
        db.refresh(cambio)
        return cambio
    
    
    @staticmethod
    def get_by_token(db: Session, token: str) -> Optional[CambioCorreoPendiente]:
        """Busca un cambio pendiente por token."""
        return db.query(CambioCorreoPendiente).filter(
            and_(
                CambioCorreoPendiente.token_validacion == token,
                CambioCorreoPendiente.estado == 'pendiente',
                CambioCorreoPendiente.token_expiracion > datetime.now(timezone.utc)
            )
        ).first()
    
    
    @staticmethod
    def get_pendiente_by_usuario(db: Session, usuario_id: int) -> Optional[CambioCorreoPendiente]:
        """Busca un cambio pendiente activo del usuario."""
        return db.query(CambioCorreoPendiente).filter(
            and_(
                CambioCorreoPendiente.usuario_id == usuario_id,
                CambioCorreoPendiente.estado == 'pendiente',
                CambioCorreoPendiente.token_expiracion > datetime.now(timezone.utc)
            )
        ).first()
    
    
    @staticmethod
    def marcar_como_validado(db: Session, cambio: CambioCorreoPendiente) -> CambioCorreoPendiente:
        """Marca un cambio como validado."""
        cambio.estado = 'validado'
        db.commit()
        db.refresh(cambio)
        return cambio
    
    
    @staticmethod
    def cancelar_cambio(db: Session, cambio: CambioCorreoPendiente) -> CambioCorreoPendiente:
        """Cancela un cambio pendiente."""
        cambio.estado = 'cancelado'
        db.commit()
        db.refresh(cambio)
        return cambio
    
    
    @staticmethod
    def limpiar_cambios_expirados(db: Session) -> int:
        """Marca como expirados los cambios que superaron su tiempo límite."""
        ahora = datetime.now(timezone.utc)
        
        count = db.query(CambioCorreoPendiente).filter(
            and_(
                CambioCorreoPendiente.estado == 'pendiente',
                CambioCorreoPendiente.token_expiracion < ahora
            )
        ).update({"estado": "expirado"})
        
        db.commit()
        return count