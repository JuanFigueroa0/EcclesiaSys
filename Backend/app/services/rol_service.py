from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List

from app.repositories.rol import RolRepository
from app.repositories.usuario_rol import UsuarioRolRepository
from app.repositories.rol_permiso import RolPermisoRepository
from app.schemas.rol import RolCreate, RolUpdate


class RolService:
    """
    Servicio para la lógica de negocio de roles.
    """
    
    @staticmethod
    def listar_roles(db: Session):
        """Lista todos los roles del sistema"""
        return RolRepository.get_all(db)
    
    @staticmethod
    def obtener_rol_por_id(db: Session, rol_id: int):
        """Obtiene un rol por su ID"""
        rol = RolRepository.get_by_id(db, rol_id)
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rol no encontrado"
            )
        return rol
    
    @staticmethod
    def crear_rol(db: Session, rol_data: RolCreate):
        """
        Crea un nuevo rol.
        Solo Superadmin puede crear roles.
        """
        # Verificar que el nombre no exista
        existe = RolRepository.get_by_nombre(db, rol_data.nombre)
        if existe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un rol con el nombre '{rol_data.nombre}'"
            )
        
        # Crear rol
        return RolRepository.create(
            db=db,
            nombre=rol_data.nombre,
            descripcion=rol_data.descripcion,
            es_sistema=rol_data.es_sistema
        )
    
    @staticmethod
    def actualizar_rol(db: Session, rol_id: int, rol_data: RolUpdate):
        """
        Actualiza un rol existente.
        Solo Superadmin puede actualizar roles.
        """
        rol = RolRepository.get_by_id(db, rol_id)
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rol no encontrado"
            )
        
        # No permitir editar roles de sistema
        if rol.es_sistema:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No se pueden editar roles del sistema"
            )
        
        # Verificar nombre único
        if rol_data.nombre and rol_data.nombre != rol.nombre:
            existe = RolRepository.get_by_nombre(db, rol_data.nombre)
            if existe:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe un rol con el nombre '{rol_data.nombre}'"
                )
        
        # Actualizar campos
        if rol_data.nombre:
            rol.nombre = rol_data.nombre
        if rol_data.descripcion is not None:
            rol.descripcion = rol_data.descripcion
        
        db.commit()
        db.refresh(rol)
        return rol
    
    @staticmethod
    def eliminar_rol(db: Session, rol_id: int):
        """
        Elimina un rol.
        Solo Superadmin puede eliminar roles.
        No se pueden eliminar roles de sistema.
        """
        # ✅ CORREGIDO
        from app.models.usuario_rol import UsuarioRol
        
        rol = RolRepository.get_by_id(db, rol_id)
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rol no encontrado"
            )
        
        # No permitir eliminar roles de sistema
        if rol.es_sistema:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No se pueden eliminar roles del sistema"
            )
        
        # Verificar que no tenga usuarios asignados
        usuarios_count = db.query(UsuarioRol).filter(
            UsuarioRol.rol_id == rol_id,
            UsuarioRol.activo == True
        ).count()
        
        if usuarios_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede eliminar el rol porque tiene {usuarios_count} usuario(s) asignado(s)"
            )
        
        db.delete(rol)
        db.commit()
        
        return {"mensaje": f"Rol '{rol.nombre}' eliminado exitosamente"}
    
    @staticmethod
    def asignar_rol_a_usuario(db: Session, usuario_id: int, rol_id: int):
        """Asigna un rol a un usuario"""
        from app.repositories.usuario import UsuarioRepository
        
        # Verificar que el usuario existe
        usuario = UsuarioRepository.get_by_id(db, usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Verificar que el rol existe
        rol = RolRepository.get_by_id(db, rol_id)
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rol no encontrado"
            )
        
        # Asignar rol
        relacion = UsuarioRolRepository.asignar_rol(db, usuario_id, rol_id)
        
        return {
            "mensaje": f"Rol '{rol.nombre}' asignado al usuario {usuario.correo}",
            "usuario_id": usuario_id,
            "rol_id": rol_id
        }
    
    @staticmethod
    def remover_rol_de_usuario(db: Session, usuario_id: int, rol_id: int):
        """Remueve un rol de un usuario"""
        removido = UsuarioRolRepository.remover_rol(db, usuario_id, rol_id)
        
        if not removido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El usuario no tiene asignado ese rol"
            )
        
        return {
            "mensaje": "Rol removido del usuario exitosamente",
            "usuario_id": usuario_id,
            "rol_id": rol_id
        }
    
    @staticmethod
    def obtener_usuarios_por_rol(db: Session, rol_id: int):
        """Obtiene todos los usuarios que tienen un rol específico"""
        rol = RolRepository.get_by_id(db, rol_id)
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rol no encontrado"
            )
        
        # ✅ Retorna lista de usuarios (objetos Usuario)
        return UsuarioRolRepository.get_usuarios_por_rol(db, rol_id)