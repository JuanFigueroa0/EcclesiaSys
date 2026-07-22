export interface Certificado {
  id: number;
  codigo: string;
  tipo: string; // 'bautismo' | 'confirmacion' | 'matrimonio' | 'primera_comunion'
  persona_nombre: string;
  fecha_emision: string;
  solicitante: string;
  estado: string; // 'emitido' | 'anulado'
}
