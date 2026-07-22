export interface Persona {
  id: number;
  primer_nombre: string;
  segundo_nombre?: string;
  primer_apellido: string;
  segundo_apellido?: string;
  tipo_documento: string;
  numero_documento: string;
  estado_civil?: string;
  fecha_nacimiento?: string;
  lugar_nacimiento?: string;
  sexo?: string;
  sacramentos?: number;
  tiene_usuario?: boolean;
}
