export interface AuditoriaLog {
  id: number;
  usuario: string;
  accion: string; // 'CREAR' | 'EDITAR' | 'ELIMINAR' | 'LOGIN' | 'EMISION_CERTIFICADO'
  modulo: string;
  detalle: string;
  ip: string;
  fecha: string;
}
