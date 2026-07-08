from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.persona import PersonaRepository
from app.repositories.persona_usuario import PersonaUsuarioRepository
from app.repositories.usuario import UsuarioRepository
from app.schemas.persona import PersonaCreate, PersonaUpdate


class PersonaService:
    """
    Servicio para la lógica de negocio de personas (perfiles).
    """
    
    @staticmethod
    def crear_perfil_usuario(db: Session, usuario_id: int, perfil_data: PersonaCreate):
        """
        Crea el perfil (persona) asociado a un usuario.
        Solo se puede crear una vez.
        """
        # Verificar que el usuario existe
        usuario = UsuarioRepository.get_by_id(db, usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Verificar que no tenga perfil ya creado
        perfil_existente = PersonaRepository.get_by_usuario_id(db, usuario_id)
        if perfil_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este usuario ya tiene un perfil creado. Usa PUT /usuarios/me/perfil para actualizarlo."
            )
        
        # Verificar que el documento no esté registrado (si aplica)
        if perfil_data.tipo_documento != 'sin_documento' and perfil_data.numero_documento:
            documento_existente = PersonaRepository.get_by_documento(
                db,
                perfil_data.tipo_documento,
                perfil_data.numero_documento
            )
            if documento_existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Este documento ya está registrado en el sistema"
                )
        
        # Crear persona 
        nueva_persona = PersonaRepository.create(
            db=db,
            primer_nombre=perfil_data.primer_nombre,
            segundo_nombre=perfil_data.segundo_nombre,
            primer_apellido=perfil_data.primer_apellido,
            segundo_apellido=perfil_data.segundo_apellido,
            fecha_nacimiento=perfil_data.fecha_nacimiento,
            sexo=perfil_data.sexo,
            lugar_nacimiento=perfil_data.lugar_nacimiento,
            region=perfil_data.region, 
            departamento=perfil_data.departamento,  
            municipio=perfil_data.municipio,  
            tipo_documento=perfil_data.tipo_documento,
            numero_documento=perfil_data.numero_documento,
            estado_civil=perfil_data.estado_civil,
            tiene_usuario=True
        )
        
        # Vincular persona con usuario
        PersonaUsuarioRepository.create(
            db=db,
            persona_id=nueva_persona.id,
            usuario_id=usuario_id
        )
        
        # Marcar perfil como completo
        UsuarioRepository.marcar_perfil_completo(db, usuario)
        
        return nueva_persona
    
    @staticmethod
    def actualizar_perfil_usuario(db: Session, usuario_id: int, perfil_data: PersonaUpdate):
        """
        Actualiza el perfil (persona) de un usuario.
        """
        # Obtener la persona asociada al usuario
        persona = PersonaRepository.get_by_usuario_id(db, usuario_id)
        
        if not persona:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No tienes un perfil creado. Usa POST /usuarios/me/perfil para crearlo."
            )
        
        # Preparar datos para actualizar
        datos_actualizacion = {}
        
        if perfil_data.primer_nombre:
            datos_actualizacion['primer_nombre'] = perfil_data.primer_nombre
        
        if perfil_data.segundo_nombre is not None:
            datos_actualizacion['segundo_nombre'] = perfil_data.segundo_nombre
        
        if perfil_data.primer_apellido:
            datos_actualizacion['primer_apellido'] = perfil_data.primer_apellido
        
        if perfil_data.segundo_apellido is not None:
            datos_actualizacion['segundo_apellido'] = perfil_data.segundo_apellido
        
        if perfil_data.fecha_nacimiento:
            datos_actualizacion['fecha_nacimiento'] = perfil_data.fecha_nacimiento
        
        if perfil_data.sexo:
            datos_actualizacion['sexo'] = perfil_data.sexo
        
        if perfil_data.lugar_nacimiento:
            datos_actualizacion['lugar_nacimiento'] = perfil_data.lugar_nacimiento
        
        if perfil_data.region is not None:
            datos_actualizacion['region'] = perfil_data.region
        
        if perfil_data.departamento is not None:
            datos_actualizacion['departamento'] = perfil_data.departamento
        
        if perfil_data.municipio is not None:
            datos_actualizacion['municipio'] = perfil_data.municipio
        
        if perfil_data.tipo_documento:
            datos_actualizacion['tipo_documento'] = perfil_data.tipo_documento
        
        if perfil_data.numero_documento:
            # Verificar que el documento no esté en uso por otra persona
            if perfil_data.tipo_documento and perfil_data.tipo_documento != 'sin_documento':
                documento_existente = PersonaRepository.get_by_documento(
                    db,
                    perfil_data.tipo_documento,
                    perfil_data.numero_documento
                )
                if documento_existente and documento_existente.id != persona.id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Este documento ya está registrado por otra persona"
                    )
            
            datos_actualizacion['numero_documento'] = perfil_data.numero_documento
        
        if perfil_data.estado_civil:
            datos_actualizacion['estado_civil'] = perfil_data.estado_civil
        
        # Actualizar persona
        persona_actualizada = PersonaRepository.update(
            db=db,
            persona=persona,
            **datos_actualizacion
        )
        
        return persona_actualizada
    
    @staticmethod
    def obtener_perfil_usuario(db: Session, usuario_id: int):
        persona = PersonaRepository.get_by_usuario_id(db, usuario_id)

        if not persona:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tienes un perfil creado"
        )

        return persona