export interface Curso {
  id: number;
  nombre: string;
  sacramento: string;
  catequista: string;
  fecha_inicio: string;
  fecha_fin: string;
  estado: string; // 'abierto' | 'en_curso' | 'finalizado'
  inscritos: number;
}
