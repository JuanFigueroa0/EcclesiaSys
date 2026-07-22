export interface ConfiguracionParroquial {
  nombre_parroquia: string;
  direccion: string;
  telefono: string;
  email_parroquia: string;
  parroco_actual: string;
  plantilla_activa: string;
  incluir_qr: boolean;
  incluir_sello: boolean;
  dias_retencion_docs: number;
  notif_email: boolean;
  notif_telegram: boolean;
  telegram_bot_token?: string;
}
