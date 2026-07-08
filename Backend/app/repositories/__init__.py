from app.repositories.usuario import UsuarioRepository
from app.repositories.rol import RolRepository
from app.repositories.usuario_rol import UsuarioRolRepository
from app.repositories.permiso import PermisoRepository
from app.repositories.rol_permiso import RolPermisoRepository
from app.repositories.modulo import ModuloRepository
from app.repositories.auditoria import AuditoriaRepository
from app.repositories.persona import PersonaRepository
from app.repositories.persona_usuario import PersonaUsuarioRepository
from app.repositories.cambio_correo import CambioCorreoRepository
from app.repositories.archivo import ArchivoRepository
from app.repositories.solicitud import SolicitudRepository

__all__ = [
    "UsuarioRepository",
    "RolRepository",
    "UsuarioRolRepository",
    "PermisoRepository",
    "RolPermisoRepository",
    "ModuloRepository",
    "AuditoriaRepository",
    "PersonaRepository",
    "PersonaUsuarioRepository",
    "CambioCorreoRepository",
    "ArchivoRepository",
    "SolicitudRepository",
]
