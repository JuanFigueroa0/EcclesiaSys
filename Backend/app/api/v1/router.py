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