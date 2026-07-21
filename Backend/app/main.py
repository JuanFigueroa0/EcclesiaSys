from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine
from app.api.v1.router import api_router

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "https://ecclesia-sys.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(api_router, prefix="/api/v1")


# Ruta raíz
@app.get("/", tags=["Root"])
def root():
    return {
        "mensaje": "ECCLESIASYS API",
        "version": settings.VERSION,
        "estado": "activo",
        "documentacion": "/api/docs"
    }


# Health check
@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }


# Evento de inicio
@app.on_event("startup")
async def startup_event():
    print(f"Iniciando {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"Entorno: {settings.ENVIRONMENT}")
    print(f"Documentación disponible en: {settings.BACKEND_URL}/api/docs")


# Evento de cierre
@app.on_event("shutdown")
async def shutdown_event():
    print(f"Cerrando {settings.PROJECT_NAME}, BYE!")
