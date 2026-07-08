from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.usuario import UsuarioRepository
from app.repositories.rol import RolRepository
from app.repositories.usuario_rol import UsuarioRolRepository
from app.repositories.persona import PersonaRepository
from app.schemas.usuario import (
    UsuarioCreate, 
    UsuarioResponse, 
    CambiarContrasena,
    CambiarEmail,
    MensajeResponse
)
from app.repositories.cambio_correo import CambioCorreoRepository
from app.schemas.usuario import CambiarEmail
from app.core.security import hash_password, verify_password
from app.utils.email import (
    enviar_email_validacion, 
    enviar_email_bienvenida, 
    enviar_email_reactivacion,
    enviar_email_cambio_correo,
    enviar_email_contrasena_cambiada,
    enviar_email_recuperacion_contrasena
)

from app.utils.rate_limiting import RateLimiter
from app.utils.tokens import generar_token_validacion, calcular_expiracion_token
import logging

logger = logging.getLogger(__name__)


class UsuarioService:
    """Servicio para la lógica de negocio de usuarios."""
    
    @staticmethod
    def crear_usuario(db: Session, usuario_data: UsuarioCreate) -> UsuarioResponse:
        """Crea un nuevo usuario en el sistema."""

        # Verificar si ya existe una cuenta activa o inactiva
        usuario_existente = UsuarioRepository.get_by_correo(db, usuario_data.correo)

        if usuario_existente:
            if usuario_existente.estado == "inactivo":
                # Cuenta inactiva — ofrecer reactivación
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "codigo":  "CUENTA_INACTIVA",
                        "mensaje": "Ya existe una cuenta con este correo pero está inactiva.",
                        "correo":  usuario_data.correo
                    }
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este correo electrónico ya está registrado"
            )

        # Crear cuenta nueva
        hash_pwd         = hash_password(usuario_data.contrasena)
        token_validacion = generar_token_validacion()
        token_expiracion = calcular_expiracion_token()

        nuevo_usuario = UsuarioRepository.create(
            db=db,
            correo=usuario_data.correo,
            hash_contrasena=hash_pwd,
            token_validacion=token_validacion,
            token_expiracion=token_expiracion
        )

        # Asignar rol "Usuario" por defecto
        try:
            from app.repositories.usuario_permiso import UsuarioPermisoRepository

            rol_usuario = RolRepository.get_by_nombre(db, "Usuario")
            if not rol_usuario:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error del sistema: Rol 'Usuario' no encontrado."
                )

            # 1. Asignar el rol
            UsuarioRolRepository.asignar_rol(
                db=db,
                usuario_id=nuevo_usuario.id,
                rol_id=rol_usuario.id
            )

            # 2. Copiar permisos del rol al usuario
            UsuarioPermisoRepository.sincronizar_permisos_desde_rol(
                db=db,
                usuario_id=nuevo_usuario.id,
                rol_id=rol_usuario.id
            )

        except HTTPException:
            raise
        except Exception as e:
            db.delete(nuevo_usuario)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al asignar rol o permisos: {str(e)}"
            )

        # Enviar email de validación
        try:
            nombre_usuario = usuario_data.correo.split('@')[0]
            envio_exitoso  = enviar_email_validacion(
                correo=nuevo_usuario.correo,
                nombre_usuario=nombre_usuario,
                token=token_validacion
            )
            if not envio_exitoso:
                logger.warning(f"No se pudo enviar email a {nuevo_usuario.correo}")
        except Exception as e:
            logger.error(f"Error al enviar email: {str(e)}")

        return nuevo_usuario
    
    @staticmethod
    def validar_email(db: Session, token: str) -> UsuarioResponse:
        """Valida el email de un usuario usando el token enviado."""
        usuario = UsuarioRepository.get_by_token_validacion(db, token)
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de validación inválido o ya ha sido usado"
            )
        
        from app.utils.tokens import token_expirado
        if token_expirado(usuario.token_expiracion):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El token de validación ha expirado. Solicita un nuevo correo de validación."
            )
        
        usuario_validado = UsuarioRepository.validar_correo(db, usuario)
        
        try:
            nombre_usuario = usuario_validado.correo.split('@')[0]
            enviar_email_bienvenida(
                correo=usuario_validado.correo,
                nombre_usuario=nombre_usuario
            )
        except Exception as e:
            logger.error(f"Error al enviar email de bienvenida: {str(e)}")
        
        return usuario_validado
    
    
    @staticmethod
    def reenviar_email_validacion(db: Session, correo: str) -> dict:
        """Reenvía el email de validación con rate limiting."""
        usuario = UsuarioRepository.get_by_correo(db, correo)
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe una cuenta con este correo electrónico"
            )
        
        if usuario.correo_validado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este correo ya ha sido validado"
            )
        
        # Rate limiting: 1 cada 5 minutos
        RateLimiter.verificar_limite_simple(
            db=db,
            usuario_id=usuario.id,
            accion='reenviar_validacion',
            minutos_espera=5
        )
        
        nuevo_token = generar_token_validacion()
        nueva_expiracion = calcular_expiracion_token()
        
        UsuarioRepository.update(
            db=db,
            usuario=usuario,
            token_validacion=nuevo_token,
            token_expiracion=nueva_expiracion
        )
        
        nombre_usuario = correo.split('@')[0]
        envio_exitoso = enviar_email_validacion(
            correo=correo,
            nombre_usuario=nombre_usuario,
            token=nuevo_token
        )
        
        if not envio_exitoso:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al enviar el correo electrónico. Intenta nuevamente más tarde."
            )
        
        return {
            "mensaje": "Se ha enviado un nuevo correo de validación. Por favor revisa tu bandeja de entrada."
        }
    
    
    @staticmethod
    def obtener_usuario_por_id(db: Session, usuario_id: int) -> UsuarioResponse:
        """Obtiene un usuario por su ID."""
        usuario = UsuarioRepository.get_by_id(db, usuario_id)
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        return usuario
    
    
    @staticmethod
    def listar_usuarios(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> list:
        """
        Lista usuarios con paginación.
        
        Args:
            db: Sesión de base de datos
            skip: Registros a saltar
            limit: Número máximo de registros
            
        Returns:
            Lista de usuarios
        """
        return UsuarioRepository.get_all(db, skip=skip, limit=limit, incluir_eliminados=False)
        
   
    
    @staticmethod
    def cambiar_contrasena(
        db: Session,
        usuario_id: int,
        contrasena_data: CambiarContrasena
    ) -> UsuarioResponse:
        """Cambia la contraseña de un usuario con rate limiting."""
        try:
            RateLimiter.verificar_y_registrar(
                db=db,
                usuario_id=usuario_id,
                accion='cambiar_contrasena',
                exito=False
            )
        except HTTPException:
            raise
        
        usuario = UsuarioService.obtener_usuario_por_id(db, usuario_id)
        
        if not verify_password(contrasena_data.contrasena_actual, usuario.hash_contrasena):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña actual es incorrecta"
            )
        
        if contrasena_data.contrasena_actual == contrasena_data.contrasena_nueva:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La nueva contraseña debe ser diferente a la actual"
            )
        
        nuevo_hash = hash_password(contrasena_data.contrasena_nueva)
        usuario_actualizado = UsuarioRepository.update(db, usuario, hash_contrasena=nuevo_hash)
        
        # Resetear contador de intentos
        from app.utils.rate_limiting import RateLimiting
        from datetime import datetime, timezone
        
        registro = db.query(RateLimiting).filter(
            RateLimiting.usuario_id == usuario_id,
            RateLimiting.accion == 'cambiar_contrasena'
        ).first()
        
        if registro:
            registro.intentos_fallidos = 0
            registro.ultimo_intento = datetime.now(timezone.utc)
            registro.bloqueado_hasta = None
            db.commit()
        
        try:
            nombre_usuario = usuario.correo.split('@')[0]
            enviar_email_contrasena_cambiada(
                correo=usuario.correo,
                nombre_usuario=nombre_usuario
            )
        except Exception as e:
            logger.error(f"Error al enviar email de confirmación: {str(e)}")
        
        return usuario_actualizado
    
    
    @staticmethod
    def eliminar_usuario(db: Session, usuario_id: int) -> UsuarioResponse:
        """Elimina lógicamente un usuario (soft delete)."""
        usuario = UsuarioService.obtener_usuario_por_id(db, usuario_id)
        return UsuarioRepository.soft_delete(db, usuario)
    
    
    @staticmethod
    def solicitar_recuperacion_contrasena(db: Session, correo: str) -> MensajeResponse:
        """Genera token de recuperación y envía email."""
        usuario = UsuarioRepository.get_by_correo(db, correo)
        
        if not usuario:
            return MensajeResponse(
                mensaje="Si el correo existe en nuestro sistema, recibirás instrucciones para restablecer tu contraseña."
            )
        
        RateLimiter.verificar_limite_simple(
            db=db,
            usuario_id=usuario.id,
            accion='solicitar_recuperacion',
            minutos_espera=5
        )
        
        if not usuario.correo_validado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debes validar tu correo antes de poder restablecer la contraseña"
            )
        
        token_recuperacion = generar_token_validacion()
        token_expiracion = calcular_expiracion_token()
        
        UsuarioRepository.update(
            db=db,
            usuario=usuario,
            token_validacion=token_recuperacion,
            token_expiracion=token_expiracion
        )
        
        try:
            nombre_usuario = correo.split('@')[0]
            
            enviar_email_recuperacion_contrasena(
                correo=correo,
                nombre_usuario=nombre_usuario,
                token=token_recuperacion
            )
        except Exception as e:
            logger.error(f"Error al enviar email de recuperación: {str(e)}")
        
        return MensajeResponse(
            mensaje="Si el correo existe en nuestro sistema, recibirás instrucciones para restablecer tu contraseña."
        )
    
    
    @staticmethod
    def restablecer_contrasena_con_confirmacion(
        db: Session,
        token: str,
        nueva_contrasena: str,
        confirmar_contrasena: str
    ) -> MensajeResponse:
        """Restablece la contraseña CON confirmación."""
        # Verificar que las contraseñas coincidan
        if nueva_contrasena != confirmar_contrasena:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Las contraseñas no coinciden"
            )
        
        # ✅ CAMBIAR ESTA LÍNEA:
        # ANTES: usuario = UsuarioRepository.get_by_token_validacion(db, token)
        # DESPUÉS:
        usuario = UsuarioRepository.get_by_token_recuperacion(db, token)
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de recuperación inválido o ya ha sido usado"
            )
        
        try:
            RateLimiter.verificar_y_registrar(
                db=db,
                usuario_id=usuario.id,
                accion='recuperar_contrasena',
                exito=False
            )
        except HTTPException:
            raise
        
        from app.utils.tokens import token_expirado
        if token_expirado(usuario.token_expiracion):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El token de recuperación ha expirado. Solicita uno nuevo."
            )
        
        nuevo_hash = hash_password(nueva_contrasena)
        UsuarioRepository.update(
            db=db,
            usuario=usuario,
            hash_contrasena=nuevo_hash,
            token_validacion=None, 
            token_expiracion=None
        )
        
        # Resetear contador
        from app.utils.rate_limiting import RateLimiting
        from datetime import datetime, timezone
        
        registro = db.query(RateLimiting).filter(
            RateLimiting.usuario_id == usuario.id,
            RateLimiting.accion == 'recuperar_contrasena'
        ).first()
        
        if registro:
            registro.intentos_fallidos = 0
            registro.ultimo_intento = datetime.now(timezone.utc)
            registro.bloqueado_hasta = None
            db.commit()
        
        try:
            nombre_usuario = usuario.correo.split('@')[0]
            enviar_email_contrasena_cambiada(
                correo=usuario.correo,
                nombre_usuario=nombre_usuario
            )
        except Exception as e:
            logger.error(f"Error al enviar email de confirmación: {str(e)}")
        
        return MensajeResponse(
            mensaje="Contraseña restablecida exitosamente. Ya puedes iniciar sesión con tu nueva contraseña."
        )

    @staticmethod
    def obtener_usuario_completo(db: Session, usuario_id: int):
        """
        Obtiene usuario con su perfil (persona) asociado.
        
        Returns:
            Usuario con relación persona cargada
        """
        usuario = UsuarioRepository.get_by_id(db, usuario_id)
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Cargar persona asociada (si existe)
        persona = PersonaRepository.get_by_usuario_id(db, usuario_id)
        
        # Agregar persona al objeto usuario
        usuario.persona = persona
        
        return usuario
    
    # CAMBIOS DE CORREO ELECTRÓNICO (NO INMEDIATOS, CON VALIDACIÓN) #
    @staticmethod
    def cambiar_email(db: Session, usuario_id: int, email_data: CambiarEmail) -> MensajeResponse:
        # Obtener usuario
        usuario = UsuarioRepository.get_by_id(db, usuario_id)
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Verificar contraseña actual
        if not verify_password(email_data.contrasena_actual, usuario.hash_contrasena):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña actual es incorrecta"
            )
        
        # Verificar que el correo actual no sea igual al nuevo
        if usuario.correo == email_data.nuevo_correo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nuevo correo es igual al actual"
            )
        
        # Verificar que el nuevo correo no esté en uso
        correo_existente = UsuarioRepository.get_by_correo(db, email_data.nuevo_correo)
        if correo_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este correo electrónico ya está en uso por otra cuenta"
            )
        
        # Generar token de validación
        token_validacion = generar_token_validacion()
        token_expiracion = calcular_expiracion_token()
        
        # Actualizar correo (marca como no validado)
        UsuarioRepository.update(
            db=db,
            usuario=usuario,
            correo=email_data.nuevo_correo,
            correo_validado=False,
            estado='pendiente_validacion',
            token_validacion=token_validacion,
            token_expiracion=token_expiracion
        )
        
        # Enviar email al nuevo correo
        try:
            nombre_usuario = email_data.nuevo_correo.split('@')[0]
            enviar_email_cambio_correo(
                correo=email_data.nuevo_correo,
                nombre_usuario=nombre_usuario,
                token=token_validacion
            )
        except Exception as e:
            logger.error(f"Error al enviar email de cambio de correo: {str(e)}")
        
        return MensajeResponse(
            mensaje=f"Se ha enviado un correo de validación a {email_data.nuevo_correo}. "
                    "Por favor, valida tu nuevo correo para poder iniciar sesión."
        )
    
    # CAMBIOS DE CONTRASEÑA#
    @staticmethod
    def cambiar_contrasena(
        db: Session,
        usuario_id: int,
        contrasena_data: CambiarContrasena
    ) -> MensajeResponse:
        usuario = UsuarioRepository.get_by_id(db, usuario_id)
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Verificar contraseña actual
        if not verify_password(contrasena_data.contrasena_actual, usuario.hash_contrasena):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña actual es incorrecta"
            )
        
        # Verificar que la nueva contraseña sea diferente
        if verify_password(contrasena_data.contrasena_nueva, usuario.hash_contrasena):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La nueva contraseña debe ser diferente a la actual"
            )
        
        # Actualizar contraseña
        nuevo_hash = hash_password(contrasena_data.contrasena_nueva)
        
        UsuarioRepository.update(
            db=db,
            usuario=usuario,
            hash_contrasena=nuevo_hash
        )
        
        return MensajeResponse(
            mensaje="Contraseña actualizada exitosamente"
        )
    
    # ELIMINACIÓN DE USUARIOS (SOFT DELETE) #
    @staticmethod
    def eliminar_usuario(db: Session, usuario_id: int) -> MensajeResponse:
        usuario = UsuarioRepository.get_by_id(db, usuario_id)
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Soft delete
        UsuarioRepository.soft_delete(db, usuario)
        
        return MensajeResponse(
            mensaje="Tu cuenta ha sido eliminada exitosamente. "
                    "Si deseas volver, puedes registrarte nuevamente con el mismo correo."
        )

    @staticmethod
    def cambiar_email(
        db: Session,
        usuario_id: int,
        email_data: CambiarEmail
    ) -> MensajeResponse:
        # Obtener usuario
        usuario = UsuarioService.obtener_usuario_por_id(db, usuario_id)
        
        # Verificar contraseña actual
        if not verify_password(email_data.contrasena_actual, usuario.hash_contrasena):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña actual es incorrecta"
            )
        
        # Verificar que el nuevo correo sea diferente
        if email_data.nuevo_correo == usuario.correo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nuevo correo es igual al actual"
            )
        
        # Verificar que el nuevo correo no esté en uso
        correo_existente = UsuarioRepository.get_by_correo(db, email_data.nuevo_correo)
        if correo_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este correo electrónico ya está en uso"
            )
        
        # Cancelar cualquier cambio pendiente anterior
        cambio_anterior = CambioCorreoRepository.get_pendiente_by_usuario(db, usuario_id)
        if cambio_anterior:
            CambioCorreoRepository.cancelar_cambio(db, cambio_anterior)
        
        # Generar token de validación
        token_validacion = generar_token_validacion()
        token_expiracion = calcular_expiracion_token()
        
        # Crear registro de cambio pendiente
        CambioCorreoRepository.crear_cambio_pendiente(
            db=db,
            usuario_id=usuario_id,
            correo_anterior=usuario.correo,
            correo_nuevo=email_data.nuevo_correo,
            token_validacion=token_validacion,
            token_expiracion=token_expiracion
        )
        
        # Enviar email de validación al NUEVO correo
        try:
            from app.utils.email import enviar_email_validacion_cambio_correo
            nombre_usuario = usuario.correo.split('@')[0]
            
            envio_exitoso = enviar_email_validacion_cambio_correo(
                correo_nuevo=email_data.nuevo_correo,
                nombre_usuario=nombre_usuario,
                token=token_validacion
            )
            
            if not envio_exitoso:
                logger.warning(f"No se pudo enviar email de validación a {email_data.nuevo_correo}")
        
        except Exception as e:
            logger.error(f"Error al enviar email de validación: {str(e)}")
        
        return MensajeResponse(
            mensaje=f"Se ha enviado un correo de confirmación a {email_data.nuevo_correo}. "
                    f"Tu correo NO cambiará hasta que confirmes el nuevo correo."
        )
    
    
    @staticmethod
    def validar_cambio_correo(db: Session, token: str) -> MensajeResponse:
        # Buscar cambio pendiente por token
        cambio = CambioCorreoRepository.get_by_token(db, token)
        
        if not cambio:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de validación inválido o expirado"
            )
        
        # Verificar que el token no haya expirado
        from app.utils.tokens import token_expirado
        if token_expirado(cambio.token_expiracion):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El token de validación ha expirado. Solicita un nuevo cambio de correo."
            )
        
        #Verificar que el nuevo correo no esté en uso (por si acaso)
        correo_existente = UsuarioRepository.get_by_correo(db, cambio.correo_nuevo)
        if correo_existente and correo_existente.id != cambio.usuario_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este correo electrónico ya está en uso"
            )
        
        # Obtener usuario
        usuario = UsuarioRepository.get_by_id(db, cambio.usuario_id)
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Guardar correo anterior para notificación
        correo_anterior = usuario.correo
        
        # EFECTUAR EL CAMBIO DE CORREO
        UsuarioRepository.update(
            db=db,
            usuario=usuario,
            correo=cambio.correo_nuevo
        )
        
        # Marcar cambio como validado
        CambioCorreoRepository.marcar_como_validado(db, cambio)
        
        # Enviar notificación al correo anterior
        try:
            from app.utils.email import enviar_email_notificacion_cambio_correo
            nombre_usuario = correo_anterior.split('@')[0]
            
            enviar_email_notificacion_cambio_correo(
                correo_anterior=correo_anterior,
                nombre_usuario=nombre_usuario,
                correo_nuevo=cambio.correo_nuevo
            )
        except Exception as e:
            logger.error(f"Error al enviar email de notificación: {str(e)}")
        
        return MensajeResponse(
            mensaje=f"¡Correo actualizado exitosamente! A partir de ahora usa {cambio.correo_nuevo} para iniciar sesión."
        )
    
    @staticmethod
    def reactivar_cuenta(db: Session, correo: str) -> MensajeResponse:
        """
        Reactiva una cuenta inactiva.
        Genera nuevo token de validación y envía correo.
        El usuario debe validar su correo y luego
        usar 'Olvidé mi contraseña' para acceder.
        """
        usuario = UsuarioRepository.get_by_correo(db, correo)

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontró una cuenta con este correo"
            )

        if usuario.estado != "inactivo":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Esta cuenta no está inactiva"
            )

        # Generar token de validación
        token_validacion = generar_token_validacion()
        token_expiracion = calcular_expiracion_token()

        # Reactivar: pasar a pendiente_validacion
        UsuarioRepository.update(
            db=db,
            usuario=usuario,
            estado='pendiente_validacion',
            correo_validado=False,
            token_validacion=token_validacion,
            token_expiracion=token_expiracion
        )

        # Enviar email de reactivación
        try:
            nombre_usuario = correo.split('@')[0]
            enviar_email_reactivacion(
                correo=correo,
                nombre_usuario=nombre_usuario,
                token=token_validacion
            )
        except Exception as e:
            logger.error(f"Error al enviar email de reactivación: {str(e)}")

        return MensajeResponse(
            mensaje="Cuenta en proceso de reactivación. Revisa tu correo para "
                    "validarla y luego usa 'Olvidé mi contraseña' para acceder."
        )
        """
        Reactiva una cuenta eliminada.
        No requiere contraseña — se envía email de validación
        y el usuario establece su contraseña via recuperación.
        """
        usuario = UsuarioRepository.get_by_correo_incluir_eliminados(db, correo)

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontró la cuenta"
            )

        if usuario.eliminado_at is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Esta cuenta no está eliminada"
            )

        # Generar nuevo token de validación
        token_validacion = generar_token_validacion()
        token_expiracion = calcular_expiracion_token()

        # Reactivar con contraseña temporal (el usuario la cambiará)
        from app.core.security import hash_password as hp
        import secrets
        contrasena_temporal = secrets.token_urlsafe(16)

        usuario_reactivado = UsuarioRepository.reactivar_usuario(
            db=db,
            usuario=usuario,
            nuevo_hash_contrasena=hp(contrasena_temporal),
            token_validacion=token_validacion,
            token_expiracion=token_expiracion
        )

        # Enviar email de reactivación con link de validación
        try:
            nombre_usuario = correo.split('@')[0]
            enviar_email_reactivacion(
                correo=correo,
                nombre_usuario=nombre_usuario,
                token=token_validacion
            )
        except Exception as e:
            logger.error(f"Error al enviar email de reactivación: {str(e)}")

        return usuario_reactivado