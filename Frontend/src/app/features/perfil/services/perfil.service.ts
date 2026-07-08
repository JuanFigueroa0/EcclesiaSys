import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../environments/environment';
import { BehaviorSubject, tap, Observable, of, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable({
  providedIn: 'root',
})
export class PerfilService {

  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  // =========================
  // CACHE
  // =========================
  private perfilSubject = new BehaviorSubject<any>(null);
  private usuarioSubject = new BehaviorSubject<any>(null);
  private perfilNotFound = false;

  perfil$ = this.perfilSubject.asObservable();

  getPerfilSnapshot() {
    return this.perfilSubject.value;
  }

  getMeSnapshot() {
    return this.usuarioSubject.value;
  }

  isPerfilNotFound(): boolean {
    return this.perfilNotFound;
  }

  // =========================
  // PERFIL
  // =========================
  getPerfil(force = false): Observable<any> {

    if (!force && this.perfilSubject.value) {
      return of(this.perfilSubject.value);
    }

    if (!force && this.perfilNotFound) {
      return of(null);
    }

    return this.http.get(`${this.apiUrl}/usuarios/me/perfil`).pipe(
      tap((data: any) => {
        this.perfilNotFound = false;
        this.perfilSubject.next(data);
      }),
      catchError((err) => {
        if (err.status === 404) {
          this.perfilNotFound = true;
          return of(null);
        }
        return throwError(() => err);
      })
    );
  }

  crearPerfil(data: any) {
    return this.http.post(`${this.apiUrl}/usuarios/me/perfil`, data).pipe(
      tap((res: any) => this.perfilSubject.next(res))
    );
  }

  actualizarPerfil(data: any) {
    return this.http.put(`${this.apiUrl}/usuarios/me/perfil`, data).pipe(
      tap((res: any) => this.perfilSubject.next(res))
    );
  }

  // CUENTA
  getMe(force = false): Observable<any> {
    if (!force && this.usuarioSubject.value) {
      return of(this.usuarioSubject.value);
    }

    return this.http.get(`${this.apiUrl}/usuarios/me`).pipe(
      tap((data: any) => this.usuarioSubject.next(data))
    );
  }

  cambiarEmail(data: any) {
    return this.http.put(`${this.apiUrl}/usuarios/me/email`, data);
  }

  cambiarPassword(data: any) {
    return this.http.put(`${this.apiUrl}/usuarios/me/password`, data);
  }

  // SESIONES
  getSesiones() {
    return this.http.get(`${this.apiUrl}/auth/sesiones`);
  }

  // Limpia el cache del perfil (usar en logout o cuando cambia la sesión)
  clearCache() {
    this.perfilSubject.next(null);
    this.usuarioSubject.next(null);
    this.perfilNotFound = false;
  }

}
