from sqlalchemy.orm import Session
from app.models.archivo import Archivo
from app.schemas.archivo import ArchivoCreate


class ArchivoRepository:

    @staticmethod
    def crear(db: Session, datos: dict) -> Archivo:
        """Crea un registro de archivo en BD con los datos de Cloudinary."""
        archivo = Archivo(
            cloudinary_public_id = datos["cloudinary_public_id"],
            cloudinary_url       = datos["cloudinary_url"],
            tipo_archivo         = datos["tipo_archivo"],
            categoria            = datos.get("categoria"),
            nombre_original      = datos.get("nombre_original"),
            tamanio_bytes        = datos.get("tamanio_bytes"),
            descripcion          = datos.get("descripcion"),
        )
        db.add(archivo)
        db.commit()
        db.refresh(archivo)
        return archivo

    @staticmethod
    def get_by_id(db: Session, archivo_id: int):
        return db.query(Archivo).filter(Archivo.id == archivo_id).first()

    @staticmethod
    def get_by_public_id(db: Session, public_id: str):
        return db.query(Archivo).filter(
            Archivo.cloudinary_public_id == public_id
        ).first()