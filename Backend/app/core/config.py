from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Información del proyecto
    PROJECT_NAME: str
    VERSION: str
    DESCRIPTION: str
    
    # Base de datos
    DATABASE_URL: str
    
    # Seguridad JWT
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES : int
    REFRESH_TOKEN_EXPIRE_DAYS: int 

    
    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    
    # Configuración de Email
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_FROM_EMAIL: str
    SMTP_FROM_NAME: str
    
    # URLs de la aplicación
    FRONTEND_URL: str
    BACKEND_URL: str
    
    # Validación de email
    EMAIL_TOKEN_EXPIRE_HOURS: int
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS : int

    
    # Entorno
    ENVIRONMENT: str
    DEBUG: bool
    
    # CORS
    ALLOWED_ORIGINS: list
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()