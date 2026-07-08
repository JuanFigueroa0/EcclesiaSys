from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List

from app.repositories.permiso import PermisoRepository
from app.repositories.rol_permiso import RolPermisoRepository
from app.schemas.permiso import PermisoCreate, PermisoUpdate


class PermisoService:
    """
    Servicio para la lógica de negocio de permisos.
    """
    
    @staticmethod
    def listar_permisos(db: Session, activos_solo: bool = True):
        """Lista todos los permisos del sistema"""
        return PermisoRepository.get_all(db, activos_solo=activos_solo)
    
    @staticmethod
    def obtener_permiso_por_id(db: Session, permiso_id: int):
        """Obtiene un permiso por su ID"""
        permiso = PermisoRepository.get_by_id(db, permiso_id)
        if not permiso:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permiso no encontrado"
            )
        return permiso
    
    @staticmethod
    def obtener_permiso_por_codigo(db: Session, codigo: str):
        """Obtiene un permiso por su código"""
        permiso = PermisoRepository.get_by_codigo(db, codigo)
        if not permiso:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permiso con código '{codigo}' no encontrado"
            )
        return permiso
    
    @staticmethod
    def listar_permisos_por_modulo(db: Session, modulo_id: int):
        """Lista permisos de un módulo específico"""
        from app.repositories.modulo import ModuloRepository
        from app.models.permiso import Permiso
        
        # Verificar que el módulo existe
        modulo = ModuloRepository.get_by_id(db, modulo_id)
        if not modulo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Módulo no encontrado"
            )
        
        # Query correcto
        permisos = db.query(Permiso).filter(
            Permiso.modulo_id == modulo_id,
            Permiso.activo == True
        ).all()
        
        return permisos
    
    @staticmethod
    def crear_permiso(db: Session, permiso_data: PermisoCreate):
        """
        Crea un nuevo permiso.
        Solo Superadmin puede crear permisos.
        """
        # Verificar que el código no exista
        existe = PermisoRepository.get_by_codigo(db, permiso_data.codigo)
        if existe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un permiso con el código '{permiso_data.codigo}'"
            )
        
        # Verificar que el módulo existe (si se especificó)
        if permiso_data.modulo_id:
            from app.repositories.modulo import ModuloRepository
            modulo = ModuloRepository.get_by_id(db, permiso_data.modulo_id)
            if not modulo:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Módulo no encontrado"
                )
        
        # Crear permiso
        return PermisoRepository.create(
            db=db,
            codigo=permiso_data.codigo,
            nombre=permiso_data.nombre,
            descripcion=permiso_data.descripcion,
            modulo_id=permiso_data.modulo_id
        )
    
    @staticmethod
    def obtener_permisos_de_rol(db: Session, rol_id: int):
        """Obtiene todos los permisos de un rol"""
        from app.repositories.rol import RolRepository
        
        # Verificar que el rol existe
        rol = RolRepository.get_by_id(db, rol_id)
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rol no encontrado"
            )
        
        return RolPermisoRepository.get_permisos_por_rol(db, rol_id)
    
    @staticmethod
    def asignar_permisos_a_rol(db: Session, rol_id: int, permisos_ids: List[int]):
        """
        Asigna múltiples permisos a un rol.
        """
        # ✅ CORREGIDO
        from app.repositories.rol import RolRepository
        
        # Verificar que el rol existe
        rol = RolRepository.get_by_id(db, rol_id)
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rol no encontrado"
            )
        
        # Verificar que todos los permisos existen por ID (no por código)
        permisos_encontrados = []
        for permiso_id in permisos_ids:
            permiso = PermisoRepository.get_by_id(db, permiso_id)
            if permiso:
                permisos_encontrados.append(permiso)
        
        if len(permisos_encontrados) != len(permisos_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Uno o más permisos no fueron encontrados. "
                       f"IDs buscados: {permisos_ids}, encontrados: {len(permisos_encontrados)}"
            )
        
        # Asignar permisos
        relaciones = RolPermisoRepository.asignar_permisos_bulk(db, rol_id, permisos_ids)
        
        return {
            "mensaje": f"Se asignaron {len(relaciones)} permisos al rol '{rol.nombre}'",
            "rol_id": rol_id,
            "permisos_asignados": len(relaciones)
        }
    
    @staticmethod
    def remover_permiso_de_rol(db: Session, rol_id: int, permiso_id: int):
        """Remueve un permiso de un rol"""
        from app.repositories.rol import RolRepository
        
        # Verificar que el rol existe
        rol = RolRepository.get_by_id(db, rol_id)
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rol no encontrado"
            )
        
        # Verificar que el permiso existe
        permiso = PermisoRepository.get_by_id(db, permiso_id)
        if not permiso:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permiso no encontrado"
            )
        
        # Remover permiso
        removido = RolPermisoRepository.remover_permiso(db, rol_id, permiso_id)
        
        if not removido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El rol no tenía asignado ese permiso"
            )
        
        return {
            "mensaje": f"Permiso '{permiso.nombre}' removido del rol '{rol.nombre}'",
            "rol_id": rol_id,
            "permiso_id": permiso_id
        }
    
    @staticmethod
    def obtener_permisos_de_usuario(db: Session, usuario_id: int):
        """
        Obtiene TODOS los permisos efectivos de un usuario:
        - Heredados por sus roles
        - Asignados directamente
        Sin duplicados.
        """
        from app.repositories.usuario import UsuarioRepository

        usuario = UsuarioRepository.get_by_id(db, usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        # Permisos por rol
        por_rol = RolPermisoRepository.get_permisos_por_usuario(db, usuario_id)
        ids_vistos = {p.id for p in por_rol}
        resultado  = list(por_rol)

        # Permisos directos (sin duplicar)
        try:
            from app.models.usuario_permiso import UsuarioPermiso
            from app.models.permiso import Permiso

            directos = (
                db.query(Permiso)
                .join(UsuarioPermiso, UsuarioPermiso.permiso_id == Permiso.id)
                .filter(
                    UsuarioPermiso.usuario_id == usuario_id,
                    UsuarioPermiso.activo == True,
                    Permiso.activo == True,
                )
                .all()
            )
            for p in directos:
                if p.id not in ids_vistos:
                    resultado.append(p)
        except Exception:
            pass
        return resultado
    
        # ── Permisos directos de usuario ──────────────────────────

    @staticmethod
    def obtener_permisos_directos_usuario(db: Session, usuario_id: int):
        """Permisos asignados DIRECTAMENTE al usuario (no por rol)."""
        from app.models.usuario_permiso import UsuarioPermiso
        from app.models.permiso import Permiso

        return (
            db.query(Permiso)
            .join(UsuarioPermiso, UsuarioPermiso.permiso_id == Permiso.id)
            .filter(
                UsuarioPermiso.usuario_id == usuario_id,
                UsuarioPermiso.activo == True,
            )
            .all()
        )

    @staticmethod
    def asignar_permiso_directo_usuario(
        db: Session, usuario_id: int, permiso_id: int
    ):
        """Asigna un permiso directo a un usuario. Si ya existe lo reactiva."""
        from app.models.usuario_permiso import UsuarioPermiso

        existente = (
            db.query(UsuarioPermiso)
            .filter(
                UsuarioPermiso.usuario_id == usuario_id,
                UsuarioPermiso.permiso_id == permiso_id,
            )
            .first()
        )
        if existente:
            existente.activo = True
            db.commit()
            return {"mensaje": "Permiso reactivado"}

        nuevo = UsuarioPermiso(usuario_id=usuario_id, permiso_id=permiso_id)
        db.add(nuevo)
        db.commit()
        return {"mensaje": "Permiso asignado"}

    @staticmethod
    def remover_permiso_directo_usuario(
        db: Session, usuario_id: int, permiso_id: int
    ):
        """Remueve (desactiva) un permiso directo de un usuario."""
        from app.models.usuario_permiso import UsuarioPermiso

        registro = (
            db.query(UsuarioPermiso)
            .filter(
                UsuarioPermiso.usuario_id == usuario_id,
                UsuarioPermiso.permiso_id == permiso_id,
            )
            .first()
        )
        if not registro:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Permiso no encontrado")

        registro.activo = False
        db.commit()
        return {"mensaje": "Permiso removido"}

    @staticmethod
    def asignar_permisos_directos_bulk(
        db: Session, usuario_id: int, permisos_ids: list
    ):
        """Asigna múltiples permisos directos a un usuario."""
        from app.models.usuario_permiso import UsuarioPermiso

        asignados = 0
        for permiso_id in permisos_ids:
            existente = (
                db.query(UsuarioPermiso)
                .filter(
                    UsuarioPermiso.usuario_id == usuario_id,
                    UsuarioPermiso.permiso_id == permiso_id,
                )
                .first()
            )
            if existente:
                existente.activo = True
            else:
                db.add(UsuarioPermiso(usuario_id=usuario_id, permiso_id=permiso_id))
            asignados += 1

        db.commit()
        return {"mensaje": f"{asignados} permisos asignados", "asignados": asignados}