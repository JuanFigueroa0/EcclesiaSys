export interface Notificacion {
  id: number;
  titulo: string;
  mensaje: string;
  tipo: 'solicitud' | 'certificado' | 'sistema' | 'evento';
  fecha: string;
  leida: boolean;
}
