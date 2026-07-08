export interface LoginRequest {
  correo: string;
  contrasena: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  session_token: string;

  usuario_id: number;
  persona_id: number;

  correo_validado: boolean;
  perfil_completo: boolean;
  estado: string;

  roles: string[];
}

export interface Session {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  session_token: string;
  usuario_id: number;
  perfil_completo: boolean;
  correo_validado: boolean;
  estado: string;
  persona_id: number;
  roles: string[];
}

export interface RegisterRequest {
  correo: string;
  contrasena: string;
}
 
export interface RegisterResponse {
  correo: string;
  id: number;
  correo_validado: boolean;
  perfil_completo: boolean;
  estado: string;
  created_at: string;
  updated_at: string;
}
 
export interface ReactivarCuentaResponse {
  mensaje: string;
}