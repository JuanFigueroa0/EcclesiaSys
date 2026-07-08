import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


def enviar_email(
    destinatario: str,
    asunto: str,
    contenido_html: str,
    contenido_texto: Optional[str] = None
) -> bool:
    try:
        # Crear mensaje
        mensaje = MIMEMultipart("alternative")
        mensaje["Subject"] = asunto
        mensaje["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        mensaje["To"] = destinatario
        
        # Agregar versión de texto plano
        if contenido_texto:
            parte_texto = MIMEText(contenido_texto, "plain", "utf-8")
            mensaje.attach(parte_texto)
        
        # Agregar versión HTML
        parte_html = MIMEText(contenido_html, "html", "utf-8")
        mensaje.attach(parte_html)
        
        # Conectar al servidor SMTP
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as servidor:
            servidor.starttls()  # Iniciar conexión segura
            servidor.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            servidor.send_message(mensaje)
        
        logger.info(f"Email enviado correctamente a {destinatario}")
        return True
        
    except Exception as e:
        logger.error(f"Error al enviar email a {destinatario}: {str(e)}")
        return False


def enviar_email_validacion(
    correo: str,
    nombre_usuario: str,
    token: str
) -> bool:
    url_validacion = f"{settings.FRONTEND_URL}/auth/verify-email?token={token}"
    
    asunto = "Valida tu cuenta - Sistema Sacramental"
    
    # Contenido HTML
    contenido_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #4a5568;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: #f7fafc;
                padding: 30px;
                border: 1px solid #e2e8f0;
            }}
            .button {{
                display: inline-block;
                background-color: #4299e1;
                color: white;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                padding: 20px;
                color: #718096;
                font-size: 12px;
            }}
            .token {{
                background-color: #edf2f7;
                padding: 10px;
                border-left: 4px solid #4299e1;
                margin: 15px 0;
                font-family: monospace;
                word-break: break-all;
                font-size: 12px;
            }}
            .info-box {{
                background-color: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>✉️ Bienvenido al Sistema Sacramental</h1>
        </div>
        <div class="content">
            <h2>¡Hola, {nombre_usuario}!</h2>
            <p>Gracias por registrarte en nuestro sistema.</p>
            <p>Para completar tu registro, por favor valida tu correo electrónico haciendo clic en el siguiente botón:</p>
            
            <div style="text-align: center;">
                <a href="{url_validacion}" class="button">✅ Validar mi correo</a>
            </div>
            
            <p>O copia y pega el siguiente enlace en tu navegador:</p>
            <div class="token">{url_validacion}</div>
            
            <p><strong>⏰ Este enlace expirará en 24 horas.</strong></p>
            
            <p style="color: #718096; font-size: 14px;">
                Si no solicitaste esta cuenta, puedes ignorar este correo.
            </p>
        </div>
        <div class="footer">
            <p>Sistema de Gestión Sacramental Parroquial</p>
            <p>Este es un correo automático, por favor no respondas a este mensaje.</p>
        </div>
    </body>
    </html>
    """
    
    # Contenido texto plano
    contenido_texto = f"""
    ✉️ Bienvenido al Sistema Sacramental
    
    ¡Hola, {nombre_usuario}!
    
    Gracias por registrarte en nuestro sistema.
    
    Para completar tu registro, valida tu correo electrónico visitando:
    {url_validacion}
    Token: {token}
    
    Envía una petición POST a:
    {settings.BACKEND_URL}/api/v1/auth/validar-email
    
    Con el JSON:
    {{"token": "{token}"}}
    
    ⏰ Este enlace expirará en 24 horas.
    
    Si no solicitaste esta cuenta, puedes ignorar este correo.
    
    ---
    🏛️ Sistema de Gestión Sacramental Parroquial
    Este es un correo automático, por favor no respondas a este mensaje.
    """
    
    return enviar_email(correo, asunto, contenido_html, contenido_texto)


def enviar_email_bienvenida(correo: str, nombre_usuario: str) -> bool:
    # Determinar URL de login según el entorno
    url_login = f"{settings.FRONTEND_URL}/"
    
    asunto = "✅ ¡Cuenta validada exitosamente!"
    
    contenido_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #48bb78;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: #f7fafc;
                padding: 30px;
                border: 1px solid #e2e8f0;
            }}
            .button {{
                display: inline-block;
                background-color: #4299e1;
                color: white;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .success-box {{
                background-color: #d4edda;
                border-left: 4px solid #48bb78;
                padding: 15px;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>✅ ¡Cuenta Validada!</h1>
        </div>
        <div class="content">
            <h2>¡Felicitaciones, {nombre_usuario}!</h2>
            
            <div class="success-box">
                <strong>✨ Tu correo electrónico ha sido validado exitosamente.</strong>
            </div>
            
            <p>Ya puedes iniciar sesión y disfrutar de todos los servicios del sistema:</p>
            
            <ul>
                <li>📜 Solicitar certificados sacramentales</li>
                <li>📁 Gestionar tus documentos</li>
                <li>📅 Ver el calendario de eventos</li>
                <li>⚙️ Y mucho más...</li>
            </ul>
            
            <p><strong>Tu correo de acceso es:</strong> {correo}</p>
            
            <div style="text-align: center;">
                <a href="{url_login}" class="button">🔐 Iniciar Sesión</a>
            </div>
        </div>
    </body>
    </html>
    """
    
    contenido_texto = f"""
    ✅ ¡Cuenta Validada!
    
    ¡Felicitaciones, {nombre_usuario}!
    
    Tu correo electrónico ha sido validado exitosamente.
    
    Tu correo de acceso es: {correo}
    
    Ya puedes iniciar sesión en: {url_login}
    """
    
    return enviar_email(correo, asunto, contenido_html, contenido_texto)

def enviar_email_recuperacion_contrasena(
    correo: str,
    nombre_usuario: str,
    token: str
) -> bool:
    # URL de recuperación
    url_reset = f"{settings.FRONTEND_URL}/auth/reset-password?token={token}"
    asunto = "🔒 Recuperación de Contraseña - Sistema Sacramental"
    
    contenido_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #f56565;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: #f7fafc;
                padding: 30px;
                border: 1px solid #e2e8f0;
            }}
            .button {{
                display: inline-block;
                background-color: #4299e1;
                color: white;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .warning-box {{
                background-color: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin: 20px 0;
            }}
            .token {{
                background-color: #edf2f7;
                padding: 10px;
                border-left: 4px solid #4299e1;
                margin: 15px 0;
                font-family: monospace;
                word-break: break-all;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔒 Recuperación de Contraseña</h1>
        </div>
        <div class="content">
            <h2>Hola, {nombre_usuario}</h2>
            <p>Recibimos una solicitud para restablecer la contraseña de tu cuenta.</p>
            
            <p>Para crear una nueva contraseña, haz clic en el siguiente botón:</p>
            
            <div style="text-align: center;">
                <a href="{url_reset}" class="button">🔐 Restablecer Contraseña</a>
            </div>
            
            <div class="warning-box">
                <strong>⏰ Este enlace expirará en 24 horas.</strong>
            </div>
            
            <p>O copia y pega el siguiente enlace en tu navegador:</p>
            <div class="token">{url_reset}</div>
            
            <p style="color: #718096; font-size: 14px; margin-top: 30px;">
                ⚠️ Si no solicitaste este cambio, puedes ignorar este correo. 
                Tu contraseña actual permanecerá sin cambios.
            </p>
        </div>
        <div style="text-align: center; padding: 20px; color: #718096; font-size: 12px;">
            <p>Sistema de Gestión Sacramental Parroquial</p>
            <p>Este es un correo automático, por favor no respondas a este mensaje.</p>
        </div>
    </body>
    </html>
    """
    
    contenido_texto = f"""
    🔒 Recuperación de Contraseña
    
    Hola, {nombre_usuario}
    
    Recibimos una solicitud para restablecer la contraseña de tu cuenta.
    
    Para crear una nueva contraseña, visita:
    {url_reset}
    
    ⏰ Este enlace expirará en 24 horas.
    
    ⚠️ Si no solicitaste este cambio, puedes ignorar este correo.
    
    ---
    Sistema de Gestión Sacramental Parroquial
    Este es un correo automático, por favor no respondas a este mensaje.
    """
    
    return enviar_email(correo, asunto, contenido_html, contenido_texto)

def enviar_email_reactivacion(correo: str, nombre_usuario: str, token: str) -> bool:
    # URL correcta → siempre al frontend, con tipo=reactivacion
    url_validacion = f"{settings.FRONTEND_URL}/auth/verify-email?token={token}&tipo=reactivacion"

    asunto = "Reactivación de cuenta - EcclesiaSys"

    contenido_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #48bb78;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: #f7fafc;
                padding: 30px;
                border: 1px solid #e2e8f0;
            }}
            .button {{
                display: inline-block;
                background-color: #4299e1;
                color: white;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
                font-weight: bold;
            }}
            .info-box {{
                background-color: #e6ffed;
                border-left: 4px solid #48bb78;
                padding: 15px;
                margin: 20px 0;
            }}
            .warning-box {{
                background-color: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin: 20px 0;
            }}
            .token {{
                background-color: #edf2f7;
                padding: 10px;
                border-left: 4px solid #4299e1;
                margin: 15px 0;
                font-family: monospace;
                word-break: break-all;
                font-size: 12px;
            }}
            .footer {{
                text-align: center;
                padding: 20px;
                color: #718096;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔄 Reactivación de Cuenta</h1>
        </div>
        <div class="content">
            <h2>¡Hola de nuevo, {nombre_usuario}!</h2>

            <div class="info-box">
                <strong>✅ Tu cuenta está siendo reactivada</strong>
                <p style="margin: 8px 0 0 0;">
                    Hemos recibido tu solicitud de reactivación. Solo necesitas
                    validar tu correo para completar el proceso.
                </p>
            </div>

            <p>Haz clic en el siguiente botón para activar tu cuenta:</p>

            <div style="text-align: center;">
                <a href="{url_validacion}" class="button">✅ Reactivar mi cuenta</a>
            </div>

            <p>O copia y pega este enlace en tu navegador:</p>
            <div class="token">{url_validacion}</div>

            <p><strong>⏰ Este enlace expirará en 24 horas.</strong></p>

            <div class="warning-box">
                <strong>📌 Próximos pasos:</strong>
                <ol style="margin: 8px 0 0 0; padding-left: 20px;">
                    <li>Haz clic en el botón de arriba para validar tu correo</li>
                    <li>Una vez validado, usa <strong>"Olvidé mi contraseña"</strong>
                        para establecer una nueva contraseña</li>
                    <li>Ya podrás iniciar sesión normalmente</li>
                </ol>
            </div>

            <p style="color: #718096; font-size: 14px; margin-top: 20px;">
                Si no solicitaste esta reactivación, puedes ignorar este correo.
                Tu cuenta permanecerá inactiva.
            </p>
        </div>
        <div class="footer">
            <p>Sistema de Gestión Sacramental Parroquial — EcclesiaSys</p>
            <p>Este es un correo automático, por favor no respondas a este mensaje.</p>
        </div>
    </body>
    </html>
    """

    contenido_texto = f"""
    🔄 Reactivación de Cuenta — EcclesiaSys

    ¡Hola de nuevo, {nombre_usuario}!

    Tu cuenta está siendo reactivada. Para completar el proceso,
    valida tu correo visitando el siguiente enlace:

    {url_validacion}

    ⏰ Este enlace expirará en 24 horas.

    📌 Próximos pasos:
    1. Valida tu correo con el enlace de arriba
    2. Usa "Olvidé mi contraseña" para establecer una nueva contraseña
    3. Inicia sesión normalmente

    Si no solicitaste esta reactivación, ignora este correo.

    ---
    Sistema de Gestión Sacramental Parroquial — EcclesiaSys
    Este es un correo automático, por favor no respondas a este mensaje.
    """

    return enviar_email(correo, asunto, contenido_html, contenido_texto)

def enviar_email_contrasena_cambiada(
    correo: str,
    nombre_usuario: str
) -> bool:
    """
    Envía email confirmando que la contraseña fue cambiada.
    
    Args:
        correo: Email del destinatario
        nombre_usuario: Nombre del usuario
        
    Returns:
        True si se envió correctamente, False si no
    """
    asunto = "Contraseña Actualizada - EcclesiaSys"
    
    cuerpo_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4CAF50;">✅ Contraseña Actualizada</h2>
                
                <p>Hola <strong>{nombre_usuario}</strong>,</p>
                
                <p>Te confirmamos que tu contraseña ha sido actualizada exitosamente.</p>
                
                <p>Ya puedes iniciar sesión con tu nueva contraseña.</p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p style="color: #666; font-size: 0.9em;">
                    <strong>⚠️ ¿No fuiste tú?</strong><br>
                    Si no realizaste este cambio, tu cuenta podría estar comprometida. 
                    Por favor contacta con nosotros inmediatamente.
                </p>
                
                <p style="color: #999; font-size: 0.85em; margin-top: 20px;">
                    Saludos,<br>
                    El equipo de EcclesiaSys
                </p>
            </div>
        </body>
    </html>
    """
    
    cuerpo_texto = f"""
    Hola {nombre_usuario},
    
    Te confirmamos que tu contraseña ha sido actualizada exitosamente.
    
    Ya puedes iniciar sesión con tu nueva contraseña.
    
    ⚠️ Si no realizaste este cambio, contacta con nosotros inmediatamente.
    
    Saludos,
    El equipo de EcclesiaSys
    """
    
    return enviar_email(correo, asunto, cuerpo_html, cuerpo_texto)

def enviar_email_validacion_cambio_correo(
    correo_nuevo: str,
    nombre_usuario: str,
    token: str
) -> bool:
    
    asunto = "Confirma tu nuevo correo - EcclesiaSys"
    
    # URL de validación
    url_validacion = f"http://localhost:8000/api/v1/usuarios/validar-cambio-correo?token={token}"
    
    cuerpo_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4CAF50;">Confirma tu Nuevo Correo</h2>
                
                <p>Hola <strong>{nombre_usuario}</strong>,</p>
                
                <p>Recibimos una solicitud para cambiar tu correo electrónico en EcclesiaSys.</p>
                
                <p><strong>⚠️ Importante:</strong> Tu correo NO cambiará hasta que confirmes este nuevo correo.</p>
                
                <p>Haz clic en el siguiente enlace para confirmar tu nuevo correo:</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{url_validacion}" 
                       style="background-color: #4CAF50; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Confirmar Nuevo Correo
                    </a>
                </div>
                
                <p><strong>O copia y pega este enlace en tu navegador:</strong></p>
                <p style="word-break: break-all; background-color: #f5f5f5; padding: 10px; border-radius: 5px;">
                    {url_validacion}
                </p>
                
                <p style="color: #999; font-size: 0.9em;">
                    <strong>⏰ Este enlace expirará en 24 horas.</strong>
                </p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p style="color: #666; font-size: 0.9em;">
                    Si no solicitaste este cambio, ignora este correo. Tu correo permanecerá sin cambios.
                </p>
                
                <p style="color: #999; font-size: 0.85em; margin-top: 20px;">
                    Saludos,<br>
                    El equipo de EcclesiaSys
                </p>
            </div>
        </body>
    </html>
    """
    
    cuerpo_texto = f"""
    Hola {nombre_usuario},
    
    Recibimos una solicitud para cambiar tu correo electrónico.
    
    ⚠️ Tu correo NO cambiará hasta que confirmes este nuevo correo.
    
    Usa el siguiente enlace para confirmar:
    {url_validacion}
    
    Este enlace expirará en 24 horas.
    
    Si no solicitaste este cambio, ignora este correo.
    
    Saludos,
    El equipo de EcclesiaSys
    """
    
    return enviar_email(correo_nuevo, asunto, cuerpo_html, cuerpo_texto)

def enviar_email_notificacion_cambio_correo(
    correo_anterior: str,
    nombre_usuario: str,
    correo_nuevo: str
) -> bool:
    """
    Envía notificación al correo ANTERIOR confirmando el cambio exitoso.
    
    Args:
        correo_anterior: Correo anterior del usuario
        nombre_usuario: Nombre del usuario
        correo_nuevo: Nuevo correo ya validado
        
    Returns:
        True si se envió correctamente, False si no
    """
    asunto = "Tu correo ha sido actualizado - EcclesiaSys"
    
    cuerpo_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4CAF50;">✅ Correo Actualizado</h2>
                
                <p>Hola <strong>{nombre_usuario}</strong>,</p>
                
                <p>Te confirmamos que tu correo electrónico ha sido actualizado exitosamente.</p>
                
                <p><strong>Correo anterior:</strong> {correo_anterior}</p>
                <p><strong>Correo nuevo:</strong> {correo_nuevo}</p>
                
                <p>A partir de ahora deberás usar <strong>{correo_nuevo}</strong> para iniciar sesión.</p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p style="color: #666; font-size: 0.9em;">
                    <strong>⚠️ ¿No fuiste tú?</strong><br>
                    Si no realizaste este cambio, tu cuenta podría estar comprometida. 
                    Por favor contacta con nosotros inmediatamente.
                </p>
                
                <p style="color: #999; font-size: 0.85em; margin-top: 20px;">
                    Saludos,<br>
                    El equipo de EcclesiaSys
                </p>
            </div>
        </body>
    </html>
    """
    
    cuerpo_texto = f"""
    Hola {nombre_usuario},
    
    Te confirmamos que tu correo electrónico ha sido actualizado exitosamente.
    
    Correo anterior: {correo_anterior}
    Correo nuevo: {correo_nuevo}
    
    A partir de ahora deberás usar {correo_nuevo} para iniciar sesión.
    
    ⚠️ Si no realizaste este cambio, contacta con nosotros inmediatamente.
    
    Saludos,
    El equipo de EcclesiaSys
    """
    
    return enviar_email(correo_anterior, asunto, cuerpo_html, cuerpo_texto)

def enviar_email_cambio_correo(correo: str, nombre_usuario: str, token: str) -> bool:
    """
    Envía email de validación para cambio de correo.
    
    Args:
        correo: Nuevo email del usuario
        nombre_usuario: Nombre del usuario
        token: Token de validación
        
    Returns:
        True si se envió correctamente, False si falló
    """
    # URL de validación
    url_validacion = f"{settings.FRONTEND_URL}/auth/verify-email?token={token}"
    
    asunto = "Confirma tu nuevo correo electrónico - Sistema Sacramental"
    
    # Contenido HTML
    contenido_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #4299e1;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: #f7fafc;
                padding: 30px;
                border: 1px solid #e2e8f0;
            }}
            .button {{
                display: inline-block;
                background-color: #48bb78;
                color: white;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .warning-box {{
                background-color: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin: 20px 0;
            }}
            .token {{
                background-color: #edf2f7;
                padding: 10px;
                border-left: 4px solid #4299e1;
                margin: 15px 0;
                font-family: monospace;
                word-break: break-all;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📧 Cambio de Correo Electrónico</h1>
        </div>
        <div class="content">
            <h2>Hola, {nombre_usuario}!</h2>
            
            <p>Has solicitado cambiar tu correo electrónico en nuestro sistema.</p>
            
            <div class="warning-box">
                <strong>⚠️ Acción requerida</strong>
                <p>Para completar el cambio, debes validar este nuevo correo electrónico.</p>
            </div>
            
            <p>Por favor, haz clic en el siguiente botón para confirmar tu nuevo correo:</p>
            
            <div style="text-align: center;">
                <a href="{url_validacion}" class="button">✅ Validar mi nuevo correo</a>
            </div>
            
            <p>O copia y pega el siguiente enlace en tu navegador:</p>
            <div class="token">{url_validacion}</div>
            
            <p><strong>⏰ Este enlace expirará en 24 horas.</strong></p>
            
            <p style="margin-top: 30px;">
                <strong>📌 Importante:</strong><br>
                • No podrás iniciar sesión hasta que valides este correo<br>
                • Si no solicitaste este cambio, ignora este correo<br>
                • Tu correo anterior quedará disponible para otras cuentas
            </p>
            
            <p style="color: #718096; font-size: 12px; margin-top: 30px;">
                Si no solicitaste este cambio, por favor contacta al administrador inmediatamente.
            </p>
        </div>
    </body>
    </html>
    """
    
    # Contenido texto plano
    contenido_texto = f"""
    📧 Cambio de Correo Electrónico
    
    Hola, {nombre_usuario}!
    
    Has solicitado cambiar tu correo electrónico.
    
    Para completar el cambio, valida tu nuevo correo visitando:
    {url_validacion}
    
    Este enlace expirará en 24 horas.
    
    IMPORTANTE:
    - No podrás iniciar sesión hasta validar este correo
    - Si no solicitaste esto, ignora este correo
    
    ---
    Sistema de Gestión Sacramental Parroquial
    """
    
    return enviar_email(correo, asunto, contenido_html, contenido_texto)