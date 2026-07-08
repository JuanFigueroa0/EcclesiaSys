from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from datetime import datetime

from app.models.usuario import Usuario


class UsuarioRepository:
    """
    Repositorio para operaciones CRUD de usuarios.
    """
    
    @staticmethod
    def create(
        db: Session,
        correo: str,
        hash_contrasena: str,
        token_validacion: Optional[str] = None,
        token_expiracion: Optional[datetime] = None
    ) -> Usuario:
        """Crea un nuevo usuario en la base de datos."""
        usuario = Usuario(
            correo=correo,
            hash_contrasena=hash_contrasena,
            estado='pendiente_validacion',
            correo_validado=False,
            perfil_completo=False,
            token_validacion=token_validacion,
            token_expiracion=token_expiracion
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario
    
    
    @staticmethod
    def get_by_id(db: Session, usuario_id: int) -> Optional[Usuario]:
        """Busca un usuario por ID. NO incluye usuarios eliminados."""
        return db.query(Usuario).filter(
            and_(
                Usuario.id == usuario_id,
                Usuario.eliminado_at.is_(None)
            )
        ).first()
    
    
    @staticmethod
    def get_by_correo(db: Session, correo: str) -> Optional[Usuario]:
        """Busca un usuario por correo electrónico. NO incluye usuarios eliminados."""
        return db.query(Usuario).filter(
            and_(
                Usuario.correo == correo,
                Usuario.eliminado_at.is_(None)
            )
        ).first()
    
    
    @staticmethod
    def get_by_correo_incluir_eliminados(db: Session, correo: str) -> Optional[Usuario]:
        """Busca un usuario por correo electrónico. INCLUYE usuarios eliminados."""
        return db.query(Usuario).filter(Usuario.correo == correo).first()
    
    
    @staticmethod
    def get_by_token_validacion(db: Session, token: str) -> Optional[Usuario]:
        return db.query(Usuario).filter(
            and_(
                Usuario.token_validacion == token,
                Usuario.correo_validado == False,
                Usuario.eliminado_at.is_(None)
            )
        ).first()
    
    
    @staticmethod
    def get_by_token_recuperacion(db: Session, token: str) -> Optional[Usuario]:
        return db.query(Usuario).filter(
            and_(
                Usuario.token_validacion == token,
                Usuario.eliminado_at.is_(None)
            )
        ).first()
    
    
    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        incluir_eliminados: bool = False,
        estado: Optional[str] = None,
        buscar: Optional[str] = None,
        rol_id: Optional[int] = None,
    ) -> List[Usuario]:
        """Obtiene lista de usuarios con paginación y filtros."""
        from app.models.usuario_rol import UsuarioRol

        query = db.query(Usuario)

        if not incluir_eliminados:
            query = query.filter(Usuario.eliminado_at.is_(None))

        # Filtro por estado
        if estado:
            query = query.filter(Usuario.estado == estado)

        # Filtro por búsqueda de correo
        if buscar:
            query = query.filter(Usuario.correo.ilike(f"%{buscar}%"))

        # Filtro por rol — join con usuario_rol
        if rol_id:
            query = query.join(
                UsuarioRol,
                and_(
                    UsuarioRol.usuario_id == Usuario.id,
                    UsuarioRol.rol_id == rol_id,
                    UsuarioRol.activo == True
                )
            )

        return query.offset(skip).limit(limit).all()


    @staticmethod
    def count(
        db: Session,
        incluir_eliminados: bool = False,
        estado: Optional[str] = None,
        buscar: Optional[str] = None,
        rol_id: Optional[int] = None,
    ) -> int:
        """Cuenta usuarios con los mismos filtros."""
        from app.models.usuario_rol import UsuarioRol

        query = db.query(Usuario)

        if not incluir_eliminados:
            query = query.filter(Usuario.eliminado_at.is_(None))

        if estado:
            query = query.filter(Usuario.estado == estado)

        if buscar:
            query = query.filter(Usuario.correo.ilike(f"%{buscar}%"))

        if rol_id:
            query = query.join(
                UsuarioRol,
                and_(
                    UsuarioRol.usuario_id == Usuario.id,
                    UsuarioRol.rol_id == rol_id,
                    UsuarioRol.activo == True
                )
            )

        return query.count()
    
    @staticmethod
    def update(
        db: Session,
        usuario: Usuario,
        **kwargs
    ) -> Usuario:
        """Actualiza campos de un usuario."""
        for key, value in kwargs.items():
            if hasattr(usuario, key) and value is not None:
                setattr(usuario, key, value)
        
        db.commit()
        db.refresh(usuario)
        return usuario
    
    
    @staticmethod
    def soft_delete(db: Session, usuario: Usuario) -> Usuario:
        """Elimina lógicamente un usuario (soft delete)."""
        usuario.eliminado_at = datetime.utcnow()
        usuario.estado = 'inactivo'
        db.commit()
        db.refresh(usuario)
        return usuario
    
    
    @staticmethod
    def reactivar_usuario(
        db: Session,
        usuario: Usuario,
        nuevo_hash_contrasena: str,
        token_validacion: str,
        token_expiracion: datetime
    ) -> Usuario:
        """Reactiva un usuario que fue eliminado."""
        usuario.eliminado_at = None
        usuario.estado = 'pendiente_validacion'
        usuario.correo_validado = False
        usuario.hash_contrasena = nuevo_hash_contrasena
        usuario.token_validacion = token_validacion
        usuario.token_expiracion = token_expiracion
        
        db.commit()
        db.refresh(usuario)
        return usuario
    
    
    @staticmethod
    def validar_correo(db: Session, usuario: Usuario) -> Usuario:
        """Marca el correo del usuario como validado."""
        usuario.correo_validado = True
        usuario.estado = 'activo'
        usuario.token_validacion = None
        usuario.token_expiracion = None
        db.commit()
        db.refresh(usuario)
        return usuario
    
    
    @staticmethod
    def marcar_perfil_completo(db: Session, usuario: Usuario) -> Usuario:
        """Marca el perfil del usuario como completo."""
        usuario.perfil_completo = True
        db.commit()
        db.refresh(usuario)
        return usuario