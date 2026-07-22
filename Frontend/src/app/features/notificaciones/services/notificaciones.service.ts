import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, of } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { environment } from '../../../../environments/environment';
import { Notificacion } from '../models/notificacion.model';

@Injectable({
  providedIn: 'root',
})
export class NotificacionesService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/notificaciones`;

  private notificacionesSubject = new BehaviorSubject<Notificacion[] | null>(null);

  getNotificaciones(force = false): Observable<Notificacion[]> {
    if (!force && this.notificacionesSubject.value !== null) {
      return of(this.notificacionesSubject.value);
    }

    return this.http.get<Notificacion[]>(`${this.apiUrl}/`).pipe(
      tap((data) => this.notificacionesSubject.next(data || [])),
      catchError((err) => {
        console.warn('Error backend notificaciones:', err);
        this.notificacionesSubject.next([]);
        return of([]);
      })
    );
  }

  marcarComoLeida(id: number): Observable<any> {
    return this.http.put(`${this.apiUrl}/${id}/marcar-leida`, {}).pipe(
      tap(() => {
        const current = this.notificacionesSubject.value;
        if (current) {
          this.notificacionesSubject.next(
            current.map((n) => (n.id === id ? { ...n, leida: true } : n))
          );
        }
      }),
      catchError((err) => {
        console.error('Error al marcar notificacion como leida:', err);
        return of({ ok: true });
      })
    );
  }

  marcarTodasComoLeidas(): Observable<any> {
    return this.http.put(`${this.apiUrl}/marcar-todas-leidas`, {}).pipe(
      tap(() => {
        const current = this.notificacionesSubject.value;
        if (current) {
          this.notificacionesSubject.next(
            current.map((n) => ({ ...n, leida: true }))
          );
        }
      }),
      catchError((err) => {
        console.error('Error al marcar todas leidas:', err);
        return of({ ok: true });
      })
    );
  }

  clearCache(): void {
    this.notificacionesSubject.next(null);
  }
}
