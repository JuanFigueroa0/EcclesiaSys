from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Request
from datetime import timedelta, timezone, datetime
from typing import Optional
from app.models.usuario_rol import UsuarioRol  
from app.models.rol import Rol                 
from app.models.usuario import Usuario
from app.repositories.usuario import UsuarioRepository
from app.repositories.sesion import SesionRepository
from app.core.security import (
    verify_password, 
    create_access_token, 
    create_refresh_token,
    generar_session_token,
    decode_refresh_token
)
from app.models.sesion import SesionUsuario 
from app.models.persona_usuario import PersonaUsuario 
from app.models.usuario_rol import UsuarioRol         
from app.models.rol import Rol     
from app.core.config import settings
from app.schemas.auth import LoginRequest, Token, RefreshTokenRequest
from sqlalchemy import and_

class AuthService:
    """
    Servicio de autenticación con refresh tokens.
    """
    
    @staticmethod
    def login(db: Session, login_data: LoginRequest, request: Request) -> dict:
        

        # ── 1. Buscar usuario ──
        usuario = db.query(Usuario).filter(
            Usuario.correo == login_data.correo
        ).first()

        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado"
            )

        if usuario.estado == "inactivo":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "codigo":  "CUENTA_INACTIVA",
                    "mensaje": "Tu cuenta está inactiva.",
                    "correo":  login_data.correo
                }
            )

        # ── 2. Verificar contraseña ──
        if not verify_password(login_data.contrasena, usuario.hash_contrasena):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo o contraseña incorrectos"
            )

        # ── 3. Verificar estado ──
        if not usuario.correo_validado:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Por favor valida tu correo electrónico antes de iniciar sesión"
            )

        if usuario.estado == "bloqueado":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tu cuenta está bloqueada. Contacta al administrador."
            )
        

        if usuario.estado not in ("activo",):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Tu cuenta está {usuario.estado}. Contacta al administrador."
            )

        # ── 4. Obtener persona vinculada ──
        from app.models.persona_usuario import PersonaUsuario  # ajusta el import
        persona_vinculada = db.query(PersonaUsuario).filter(
            PersonaUsuario.usuario_id == usuario.id
        ).first()
        persona_id = persona_vinculada.persona_id if persona_vinculada else None

        # ── 5. Obtener roles activos ──
        
        roles_query = (
            db.query(Rol.nombre)
            .join(UsuarioRol, UsuarioRol.rol_id == Rol.id)
            .filter(
                UsuarioRol.usuario_id == usuario.id,
                UsuarioRol.activo == True
            )
            .order_by(Rol.id.desc())
            .all()
        )
        roles_lista = [r.nombre for r in roles_query]

        # ── 6. Generar tokens ──
        session_token = generar_session_token()

        access_token = create_access_token(
            data={"sub": usuario.correo},
            session_token=session_token,
            usuario_id=usuario.id,
            perfil_completo=usuario.perfil_completo,
            correo_validado=usuario.correo_validado,
            estado=usuario.estado,
            persona_id=persona_id,
            roles=roles_lista
        )

        refresh_token = create_refresh_token(
            usuario_id=usuario.id,
            session_token=session_token
        )

        # ── 7. Guardar sesión en BD ──
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", "")

        sesion = SesionUsuario(
            usuario_id=usuario.id,
            session_token=session_token,
            refresh_token=refresh_token,
            ip_address=ip_address,
            user_agent=user_agent,
            fecha_expiracion=datetime.now(timezone.utc) + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            ),
            activa=True,
            revocada=False
        )
        db.add(sesion)
        db.commit()

        # ── 8. Retornar todo ──
        return {
            "access_token":    access_token,
            "refresh_token":   refresh_token,
            "token_type":      "bearer",
            "expires_in":      settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "session_token":   session_token,
            # Espejo para el frontend
            "usuario_id":      usuario.id,
            "perfil_completo": usuario.perfil_completo,
            "correo_validado": usuario.correo_validado,
            "estado":          usuario.estado,
            "persona_id":      persona_id,
            "roles":           roles_lista
        }
    
    @staticmethod
    def refresh_access_token(db: Session, refresh_data: RefreshTokenRequest) -> dict:                    # ajusta

        # ── 1. Decodificar refresh token ──
        payload = decode_refresh_token(refresh_data.refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido o expirado"
            )

        usuario_id    = int(payload["sub"])
        session_token = payload["session_token"]

        # ── 2. Verificar sesión en BD ──
        sesion = db.query(SesionUsuario).filter(
            SesionUsuario.session_token == session_token,
            SesionUsuario.usuario_id    == usuario_id,
            SesionUsuario.activa        == True,
            SesionUsuario.revocada      == False
        ).first()

        if not sesion:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sesión no encontrada o revocada"
            )

        # ── 3. Buscar usuario ──
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario or usuario.estado != "activo":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario inactivo o no encontrado"
            )

        # ── 4. Obtener persona y roles actualizados ──
        persona_vinculada = db.query(PersonaUsuario).filter(
            PersonaUsuario.usuario_id == usuario.id
        ).first()
        persona_id = persona_vinculada.persona_id if persona_vinculada else None

        roles_query = (
            db.query(Rol.nombre)
            .join(UsuarioRol, UsuarioRol.rol_id == Rol.id)
            .filter(
                UsuarioRol.usuario_id == usuario.id,
                UsuarioRol.activo     == True
            )
            .order_by(Rol.id.desc())
            .all()
        )
        roles_lista = [r.nombre for r in roles_query]

        # ── 5. Generar nuevo access token (mismo session_token) ──
        nuevo_access_token = create_access_token(
            data={"sub": usuario.correo},
            session_token=session_token,
            usuario_id=usuario.id,
            perfil_completo=usuario.perfil_completo,
            correo_validado=usuario.correo_validado,
            estado=usuario.estado,
            persona_id=persona_id,
            roles=roles_lista
        )

        # ── 6. Actualizar fecha_ultimo_uso de la sesión ──
        sesion.fecha_ultimo_uso = datetime.now(timezone.utc)
        db.commit()

        return {
            "access_token":    nuevo_access_token,
            "refresh_token":   refresh_data.refresh_token,  # el mismo
            "token_type":      "bearer",
            "expires_in":      settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "session_token":   session_token,
            # Espejo actualizado
            "usuario_id":      usuario.id,
            "perfil_completo": usuario.perfil_completo,
            "correo_validado": usuario.correo_validado,
            "estado":          usuario.estado,
            "persona_id":      persona_id,
            "roles":           roles_lista
        }
    
    @staticmethod
    def logout(
        db: Session,
        session_token: str,
        cerrar_todas: bool = False,
        usuario_id: Optional[int] = None
    ) -> dict:
        if cerrar_todas and usuario_id:
            # Cerrar todas las sesiones del usuario excepto la actual
            count = SesionRepository.revocar_todas_sesiones_usuario(
                db=db,
                usuario_id=usuario_id,
                except_session_token=None  # Cerrar todas, incluyendo la actual
            )
            return {
                "mensaje": f"Se han cerrado {count} sesión(es) activa(s)"
            }
        else:
            # Cerrar solo esta sesión
            sesion = SesionRepository.get_by_session_token(db, session_token)
            
            if sesion:
                SesionRepository.revocar_sesion(db, sesion, "Cierre de sesión normal")
            
            return {
                "mensaje": "Sesión cerrada exitosamente"
            }
    
    # Lista las sesiones activas de un usuario
    @staticmethod
    def listar_sesiones_activas(db: Session, usuario_id: int):
        return SesionRepository.listar_sesiones_activas(db, usuario_id)