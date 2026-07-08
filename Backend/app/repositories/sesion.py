from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from datetime import datetime, timezone, timedelta

from app.models.sesion import SesionUsuario


class SesionRepository:
    """
    Repositorio para operaciones CRUD de sesiones.
    """
    
    @staticmethod
    def crear_sesion(
        db: Session,
        usuario_id: int,
        session_token: str,
        refresh_token: str,
        fecha_expiracion: datetime,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> SesionUsuario:
        """Crea una nueva sesión."""
        sesion = SesionUsuario(
            usuario_id=usuario_id,
            session_token=session_token,
            refresh_token=refresh_token,
            fecha_expiracion=fecha_expiracion,
            ip_address=ip_address,
            user_agent=user_agent,
            activa=True,
            revocada=False
        )
        db.add(sesion)
        db.commit()
        db.refresh(sesion)
        return sesion
    
    
    @staticmethod
    def get_by_session_token(db: Session, session_token: str) -> Optional[SesionUsuario]:
        """Busca sesión por session_token."""
        return db.query(SesionUsuario).filter(
            and_(
                SesionUsuario.session_token == session_token,
                SesionUsuario.activa == True,
                SesionUsuario.revocada == False,
                SesionUsuario.fecha_expiracion > datetime.now(timezone.utc)
            )
        ).first()
    
    
    @staticmethod
    def get_by_refresh_token(db: Session, refresh_token: str) -> Optional[SesionUsuario]:
        """Busca sesión por refresh_token."""
        return db.query(SesionUsuario).filter(
            and_(
                SesionUsuario.refresh_token == refresh_token,
                SesionUsuario.activa == True,
                SesionUsuario.revocada == False,
                SesionUsuario.fecha_expiracion > datetime.now(timezone.utc)
            )
        ).first()
    
    
    @staticmethod
    def actualizar_ultimo_uso(db: Session, sesion: SesionUsuario) -> SesionUsuario:
        """Actualiza la fecha de último uso de una sesión."""
        sesion.fecha_ultimo_uso = datetime.now(timezone.utc)
        db.commit()
        db.refresh(sesion)
        return sesion
    
    
    @staticmethod
    def revocar_sesion(
        db: Session, 
        sesion: SesionUsuario, 
        motivo: str = "Cierre de sesión"
    ) -> SesionUsuario:
        """Revoca una sesión."""
        sesion.activa = False
        sesion.revocada = True
        sesion.motivo_revocacion = motivo
        db.commit()
        db.refresh(sesion)
        return sesion
    
    
    @staticmethod
    def revocar_todas_sesiones_usuario(
        db: Session, 
        usuario_id: int, 
        except_session_token: Optional[str] = None
    ) -> int:
        """Revoca todas las sesiones de un usuario, excepto opcionalmente una."""
        query = db.query(SesionUsuario).filter(
            and_(
                SesionUsuario.usuario_id == usuario_id,
                SesionUsuario.activa == True
            )
        )
        
        if except_session_token:
            query = query.filter(SesionUsuario.session_token != except_session_token)
        
        count = query.update({
            "activa": False,
            "revocada": True,
            "motivo_revocacion": "Revocación masiva de sesiones"
        })
        
        db.commit()
        return count
    
    
    @staticmethod
    def limpiar_sesiones_expiradas(db: Session) -> int:
        """Elimina sesiones expiradas hace más de 30 días."""
        fecha_limite = datetime.now(timezone.utc) - timedelta(days=30)
        
        count = db.query(SesionUsuario).filter(
            SesionUsuario.fecha_expiracion < fecha_limite
        ).delete()
        
        db.commit()
        return count
    
    
    @staticmethod
    def listar_sesiones_activas(db: Session, usuario_id: int) -> List[SesionUsuario]:
        """Lista todas las sesiones activas de un usuario."""
        return db.query(SesionUsuario).filter(
            and_(
                SesionUsuario.usuario_id == usuario_id,
                SesionUsuario.activa == True,
                SesionUsuario.fecha_expiracion > datetime.now(timezone.utc)
            )
        ).order_by(SesionUsuario.fecha_ultimo_uso.desc()).all()