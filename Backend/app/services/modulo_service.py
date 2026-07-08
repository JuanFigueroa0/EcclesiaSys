from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List

from app.repositories.modulo import ModuloRepository
from app.schemas.modulo import ModuloCreate, ModuloUpdate


class ModuloService:
    """
    Servicio para la lógica de negocio de módulos.
    """
    
    @staticmethod
    def listar_modulos(db: Session, activos_solo: bool = True):
        """Lista todos los módulos del sistema"""
        return ModuloRepository.get_all(db, activos_solo=activos_solo)
    
    @staticmethod
    def obtener_modulo_por_id(db: Session, modulo_id: int):
        """Obtiene un módulo por su ID"""
        modulo = ModuloRepository.get_by_id(db, modulo_id)
        if not modulo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Módulo no encontrado"
            )
        return modulo
    
    @staticmethod
    def obtener_modulo_por_codigo(db: Session, codigo: str):
        """Obtiene un módulo por su código"""
        modulo = ModuloRepository.get_by_codigo(db, codigo)
        if not modulo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Módulo con código '{codigo}' no encontrado"
            )
        return modulo
    
    @staticmethod
    def crear_modulo(db: Session, modulo_data: ModuloCreate):
        """
        Crea un nuevo módulo.
        """
        # Verificar que el código no exista
        existe_codigo = ModuloRepository.get_by_codigo(db, modulo_data.codigo)
        if existe_codigo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un módulo con el código '{modulo_data.codigo}'"
            )
        
        # Verificar que el nombre no exista
        existe_nombre = ModuloRepository.get_by_nombre(db, modulo_data.nombre)
        if existe_nombre:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un módulo con el nombre '{modulo_data.nombre}'"
            )
        
        # Crear módulo
        return ModuloRepository.create(
            db=db,
            nombre=modulo_data.nombre,
            codigo=modulo_data.codigo,
            descripcion=modulo_data.descripcion
        )
    
    @staticmethod
    def actualizar_modulo(db: Session, modulo_id: int, modulo_data: ModuloUpdate):
        """
        Actualiza un módulo existente.
        """
        modulo = ModuloRepository.get_by_id(db, modulo_id)
        if not modulo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Módulo no encontrado"
            )
        
        # Verificar código único (si se está cambiando)
        if modulo_data.codigo and modulo_data.codigo != modulo.codigo:
            existe = ModuloRepository.get_by_codigo(db, modulo_data.codigo)
            if existe:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe un módulo con el código '{modulo_data.codigo}'"
                )
        
        # Verificar nombre único (si se está cambiando)
        if modulo_data.nombre and modulo_data.nombre != modulo.nombre:
            existe = ModuloRepository.get_by_nombre(db, modulo_data.nombre)
            if existe:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe un módulo con el nombre '{modulo_data.nombre}'"
                )
        
        # Actualizar campos
        if modulo_data.nombre:
            modulo.nombre = modulo_data.nombre
        if modulo_data.codigo:
            modulo.codigo = modulo_data.codigo
        if modulo_data.descripcion is not None:
            modulo.descripcion = modulo_data.descripcion
        if modulo_data.activo is not None:
            modulo.activo = modulo_data.activo
        
        db.commit()
        db.refresh(modulo)
        return modulo
    
    @staticmethod
    def eliminar_modulo(db: Session, modulo_id: int):
        """
        Elimina un módulo.
        """
        modulo = ModuloRepository.get_by_id(db, modulo_id)
        if not modulo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Módulo no encontrado"
            )
        
        # Verificar que no tenga permisos asociados
        from app.models.permiso import Permiso
        permisos_count = db.query(Permiso).filter(Permiso.modulo_id == modulo_id).count()
        
        if permisos_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede eliminar el módulo porque tiene {permisos_count} permiso(s) asociado(s)"
            )
        
        db.delete(modulo)
        db.commit()
        
        return {"mensaje": f"Módulo '{modulo.nombre}' eliminado exitosamente"}