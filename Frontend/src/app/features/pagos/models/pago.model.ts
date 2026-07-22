export interface Pago {
  id: number;
  referencia: string;
  concepto: string;
  monto: number;
  fiel_nombre: string;
  fecha: string;
  metodo: string; // 'efectivo' | 'transferencia' | 'tarjeta'
  estado: string; // 'completado' | 'pendiente' | 'anulado'
}
