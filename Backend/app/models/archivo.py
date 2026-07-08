from sqlalchemy import Column, BigInteger, String, Text, TIMESTAMP
from sqlalchemy.sql import func
from app.core.database import Base


class Archivo(Base):
    __tablename__ = "archivos"

    id = Column(BigInteger, primary_key=True, index=True)
    cloudinary_public_id = Column(Text, nullable=False, unique=True)
    cloudinary_url = Column(Text, nullable=False)

    tipo_archivo = Column(
        String(50),
        nullable=False
        # imagen | pdf | documento
    )

    categoria = Column(
        String(100),
        nullable=True
        # documento_identidad | certificado_externo | registro_civil | acta_defuncion
        # documento_anulacion | custodia_legal | certificado_curso | certificado_sacramento
        # foto_persona | otro
    )

    nombre_original = Column(String(255), nullable=True)
    tamanio_bytes = Column(BigInteger, nullable=True)
    descripcion = Column(Text, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())