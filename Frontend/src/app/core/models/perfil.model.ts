export interface PerfilUsuario {
  correo: string;
  id: number;
  correo_validado: boolean;
  perfil_completo: boolean;
  estado: string;
  created_at: string;

  persona: {
    primer_nombre: string;
    segundo_nombre: string;
    primer_apellido: string;
    segundo_apellido: string;

    fecha_nacimiento: string;
    sexo: string;

    lugar_nacimiento: string;
    region: string;
    departamento: string;
    municipio: string;

    tipo_documento: string;
    numero_documento: string;

    estado_civil: string;

    foto_url: string;
    foto_public_id: string;
  };

  roles: string[];
}