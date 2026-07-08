from sqlalchemy.orm import Session
from sqlalchemy import Column, BigInteger, String, Integer, DateTime
from sqlalchemy.sql import func
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import HTTPException, status

from app.core.database import Base


class RateLimiting(Base):
    __tablename__ = "rate_limiting"
    
    id = Column(BigInteger, primary_key=True, index=True)
    usuario_id = Column(BigInteger, nullable=False, index=True)
    accion = Column(String(50), nullable=False, index=True)
    ultimo_intento = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    intentos_fallidos = Column(Integer, default=0)
    bloqueado_hasta = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class RateLimiter:
    """
    Sistema de rate limiting para proteger endpoints sensibles.
    
    Límites por acción:
    - reenviar_validacion: 1 cada 5 minutos
    - cambiar_contrasena: 3 cada 15 minutos
    - recuperar_contrasena: 3 cada 15 minutos
    - login_fallido: 5 cada 15 minutos (bloquea 30 minutos)
    """
    
    LIMITES = {
        'reenviar_validacion': {
            'max_intentos': 1,
            'ventana_minutos': 5,
            'bloqueo_minutos': 5
        },
        'cambiar_contrasena': {
            'max_intentos': 3,
            'ventana_minutos': 15,
            'bloqueo_minutos': 15
        },
        'recuperar_contrasena': {
            'max_intentos': 3,
            'ventana_minutos': 15,
            'bloqueo_minutos': 15
        },
        'solicitar_recuperacion': {
            'max_intentos': 3,
            'ventana_minutos': 15,
            'bloqueo_minutos': 15
        },
        'login_fallido': {
            'max_intentos': 5,
            'ventana_minutos': 15,
            'bloqueo_minutos': 30
        }
    }
    
    @staticmethod
    def verificar_y_registrar(
        db: Session,
        usuario_id: int,
        accion: str,
        exito: bool = True
    ) -> None:
        """
        Verifica si se permite la acción y registra el intento.
        
        Args:
            db: Sesión de base de datos
            usuario_id: ID del usuario
            accion: Tipo de acción (reenviar_validacion, cambiar_contrasena, etc)
            exito: Si la acción fue exitosa
            
        Raises:
            HTTPException: Si se excede el rate limit
        """
        if accion not in RateLimiter.LIMITES:
            return  # No hay límite para esta acción
        
        config = RateLimiter.LIMITES[accion]
        ahora = datetime.now(timezone.utc)
        
        # Buscar registro existente
        registro = db.query(RateLimiting).filter(
            RateLimiting.usuario_id == usuario_id,
            RateLimiting.accion == accion
        ).first()
        
        # Si no existe, crear uno nuevo
        if not registro:
            registro = RateLimiting(
                usuario_id=usuario_id,
                accion=accion,
                ultimo_intento=ahora,
                intentos_fallidos=0 if exito else 1
            )
            db.add(registro)
            db.commit()
            return
        
        # Verificar si está bloqueado
        if registro.bloqueado_hasta and ahora < registro.bloqueado_hasta:
            tiempo_restante = registro.bloqueado_hasta - ahora
            minutos_restantes = int(tiempo_restante.total_seconds() / 60) + 1
            
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Has excedido el límite de intentos. Por favor espera {minutos_restantes} minuto(s) antes de intentar nuevamente."
            )
        
        # Si pasó la ventana de tiempo, resetear contador
        ventana = timedelta(minutes=config['ventana_minutos'])
        if ahora - registro.ultimo_intento > ventana:
            registro.intentos_fallidos = 0 if exito else 1
            registro.bloqueado_hasta = None
        else:
            # Dentro de la ventana de tiempo
            if not exito:
                registro.intentos_fallidos += 1
            
            # Verificar si excede el límite
            if registro.intentos_fallidos >= config['max_intentos']:
                registro.bloqueado_hasta = ahora + timedelta(minutes=config['bloqueo_minutos'])
                db.commit()
                
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Has excedido el límite de {config['max_intentos']} intentos en {config['ventana_minutos']} minutos. Bloqueado por {config['bloqueo_minutos']} minutos."
                )
        
        # Actualizar último intento
        registro.ultimo_intento = ahora
        db.commit()
    
    
    @staticmethod
    def verificar_limite_simple(
        db: Session,
        usuario_id: int,
        accion: str,
        minutos_espera: int = 5
    ) -> None:
        """
        Verificación simple: solo permite una acción cada X minutos.
        
        Args:
            db: Sesión de base de datos
            usuario_id: ID del usuario
            accion: Tipo de acción
            minutos_espera: Minutos mínimos entre acciones
            
        Raises:
            HTTPException: Si no ha pasado suficiente tiempo
        """
        ahora = datetime.now(timezone.utc)
        
        registro = db.query(RateLimiting).filter(
            RateLimiting.usuario_id == usuario_id,
            RateLimiting.accion == accion
        ).first()
        
        if registro:
            tiempo_transcurrido = ahora - registro.ultimo_intento
            
            if tiempo_transcurrido < timedelta(minutes=minutos_espera):
                minutos_restantes = minutos_espera - int(tiempo_transcurrido.total_seconds() / 60)
                
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Por favor espera {minutos_restantes} minuto(s) antes de realizar esta acción nuevamente."
                )
            
            # Actualizar último intento
            registro.ultimo_intento = ahora
            db.commit()
        else:
            # Crear nuevo registro
            registro = RateLimiting(
                usuario_id=usuario_id,
                accion=accion,
                ultimo_intento=ahora
            )
            db.add(registro)
            db.commit()
    
    
    @staticmethod
    def limpiar_registros_antiguos(db: Session, dias: int = 30) -> int:
        """
        Limpia registros de rate limiting más antiguos que X días.
        
        Args:
            db: Sesión de base de datos
            dias: Días de antigüedad para eliminar
            
        Returns:
            Número de registros eliminados
        """
        fecha_limite = datetime.now(timezone.utc) - timedelta(days=dias)
        
        registros_eliminados = db.query(RateLimiting).filter(
            RateLimiting.created_at < fecha_limite
        ).delete()
        
        db.commit()
        return registros_eliminados