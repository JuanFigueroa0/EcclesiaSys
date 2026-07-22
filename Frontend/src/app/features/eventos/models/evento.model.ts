export interface Evento {
  id: number;
  titulo: string;
  tipo: string; // 'misa' | 'retiro' | 'curso' | 'reunion' | 'celebracion'
  estado: string; // 'borrador' | 'publicado' | 'cerrado' | 'finalizado' | 'cancelado'
  fecha: string;
  hora: string;
  lugar: string;
  cupo: number;
  inscritos: number;
  descripcion?: string;
}
