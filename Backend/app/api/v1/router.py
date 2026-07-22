# app/api/v1/router.py
from fastapi import APIRouter

from app.api.v1.auth import endpoints as auth_endpoints
from app.api.v1.usuarios import endpoints as usuarios_endpoints
from app.api.v1.permisos import endpoints as permisos_endpoints
from app.api.v1.modulos import endpoints as modulos_endpoints
from app.api.v1.roles import endpoints as roles_endpoints
from app.api.v1.solicitudes import endpoints as solicitudes_endpoints
from app.api.v1.archivos import endpoints as archivos_endpoints
from app.api.v1.sacramentos import endpoints as sacramentos_endpoints 
from app.api.v1.personas import endpoints as personas_endpoints
from app.api.v1.eventos import endpoints as eventos_endpoints
from app.api.v1.notificaciones import endpoints as notificaciones_endpoints
from app.api.v1.configuracion import endpoints as configuracion_endpoints
from app.api.v1.certificados import endpoints as certificados_endpoints
from app.api.v1.cursos import endpoints as cursos_endpoints
from app.api.v1.pagos import endpoints as pagos_endpoints
from app.api.v1.auditoria import endpoints as auditoria_endpoints

api_router = APIRouter()

api_router.include_router(
    auth_endpoints.router,
    prefix="/auth",
    tags=["Autenticación"]
)
api_router.include_router(
    usuarios_endpoints.router,
    prefix="/usuarios",
    tags=["Usuarios"]
)
api_router.include_router(
    permisos_endpoints.router,
    prefix="/permisos",
    tags=["Permisos"]
)
api_router.include_router(
    modulos_endpoints.router,
    prefix="/modulos",
    tags=["Módulos"]
)
api_router.include_router(
    roles_endpoints.router,
    prefix="/roles",
    tags=["Roles"]
)
api_router.include_router(
    solicitudes_endpoints.router,
    prefix="/solicitudes",
    tags=["Solicitudes de Sacramento"]
)
api_router.include_router(
    archivos_endpoints.router,
    prefix="/archivos",
    tags=["Archivos"]
)
api_router.include_router(
    sacramentos_endpoints.router,
    prefix="/sacramentos",
    tags=["Sacramentos"]
)
api_router.include_router(
    personas_endpoints.router,
    prefix="/personas",
    tags=["Personas"]
)
api_router.include_router(
    eventos_endpoints.router,
    prefix="/eventos",
    tags=["Eventos"]
)
api_router.include_router(
    notificaciones_endpoints.router,
    prefix="/notificaciones",
    tags=["Notificaciones"]
)
api_router.include_router(
    configuracion_endpoints.router,
    prefix="/configuracion",
    tags=["Configuración"]
)
api_router.include_router(
    certificados_endpoints.router,
    prefix="/certificados",
    tags=["Certificados"]
)
api_router.include_router(
    cursos_endpoints.router,
    prefix="/cursos",
    tags=["Cursos"]
)
api_router.include_router(
    pagos_endpoints.router,
    prefix="/pagos",
    tags=["Pagos"]
)
api_router.include_router(
    auditoria_endpoints.router,
    prefix="/auditoria",
    tags=["Auditoría"]
)