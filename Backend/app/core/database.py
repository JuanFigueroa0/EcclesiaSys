from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verifica conexión antes de usar
    pool_size=10,        # Número de conexiones en el pool
    max_overflow=20,     # Conexiones adicionales si se necesitan
    echo=False           # Habilitar logging de SQL para depuración
)


# SESIÓN DE BASE DE DATOS
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# BASE PARA MODELOS ORM
Base = declarative_base()


# Obtener sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()