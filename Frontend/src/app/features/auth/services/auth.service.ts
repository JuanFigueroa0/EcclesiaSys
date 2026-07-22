import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { Observable, tap } from 'rxjs';

import { environment } from '../../../../environments/environment';

import {
  LoginRequest,
  AuthResponse,
  RegisterRequest,
  RegisterResponse,
  ReactivarCuentaResponse
} from '../../../core/models/auth.model';

import { TokenService } from '../../../core/services/token';
import { PerfilService } from '../../perfil/services/perfil.service';
import { VerifyEmailRequest } from '../models/verify-email-request.model';
import { ResendVerificationRequest } from '../models/resend-verification-request.model';
import { VerifyEmailResponse } from '../models/verify-email-response.model';

@Injectable({
  providedIn: 'root',
})
export class AuthService {

  private http = inject(HttpClient);
  private tokenService = inject(TokenService);
  private perfilService = inject(PerfilService);

  private apiUrl = environment.apiUrl;

  login(
    payload: LoginRequest
  ): Observable<AuthResponse> {

    return this.http.post<AuthResponse>(
      `${this.apiUrl}/auth/login`,
      payload
    ).pipe(
      tap((response) => {
        this.tokenService.saveSession(response);
      })
    );
  }

  register(payload: RegisterRequest): Observable<RegisterResponse> {
    return this.http.post<RegisterResponse>(
      `${this.apiUrl}/auth/register`, // ⚠️ ajustá si tu endpoint real es distinto
      payload
    );
  }

  reactivarCuenta(correo: string): Observable<ReactivarCuentaResponse> {
    return this.http.post<ReactivarCuentaResponse>(
      `${this.apiUrl}/auth/reactivar-cuenta`,
      { correo }
    );
  }

/**
   * Verificación de correo (link automático desde el correo)
   */
  verifyEmail(
    token: string,
    correo?: string,
    tipo?: string
  ): Observable<VerifyEmailResponse> {

    let url = `${this.apiUrl}/auth/validar-email?token=${encodeURIComponent(token)}`;

    if (correo) {
      url += `&correo=${encodeURIComponent(correo)}`;
    }

    if (tipo) {
      url += `&tipo=${encodeURIComponent(tipo)}`;
    }

    return this.http.get<VerifyEmailResponse>(url);
  }

  /**
   * Verificación manual (usuario pega el código/token)
   */
  verifyEmailManual(
    request: VerifyEmailRequest
  ): Observable<VerifyEmailResponse> {

    return this.http.post<VerifyEmailResponse>(
      `${this.apiUrl}/auth/validar-email`,
      request
    );
  }

  /**
   * Reenviar correo de verificación
   */
  resendVerificationEmail(
    request: ResendVerificationRequest
  ): Observable<VerifyEmailResponse> {

    return this.http.post<VerifyEmailResponse>(
      `${this.apiUrl}/auth/reenviar-validacion`,
      request
    );
  }

  recuperarContrasena(correo: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/auth/recuperar-contrasena`, { correo });
  }

  restablecerContrasena(token: string, contrasena_nueva: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/auth/reset-password`, { token, contrasena_nueva });
  }

  logout(): void {
    this.tokenService.clearSession();
    this.perfilService.clearCache();
  }

  isAuthenticated(): boolean {
    return this.tokenService.isLoggedIn();
  }

  getCurrentUser(): any {
    return this.tokenService.getSession();
  }

  getAccessToken(): string | null {
    return this.tokenService.getAccessToken();
  }
}