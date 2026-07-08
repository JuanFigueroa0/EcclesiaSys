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