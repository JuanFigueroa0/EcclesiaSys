import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../../../environments/environment';
import { Notificacion } from '../models/notificacion.model';

@Injectable({
  providedIn: 'root',
})
export class NotificacionesService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/notificaciones`;

  getNotificaciones(): Observable<Notificacion[]> {
    return this.http.get<Notificacion[]>(`${this.apiUrl}/`).pipe(
      catchError((err) => {
        console.warn('Error backend notificaciones:', err);
        return of([]);
      })
    );
  }

  marcarComoLeida(id: number): Observable<any> {
    return this.http.put(`${this.apiUrl}/${id}/marcar-leida`, {}).pipe(
      catchError((err) => {
        console.error('Error al marcar notificacion como leida:', err);
        return of({ ok: true });
      })
    );
  }

  marcarTodasComoLeidas(): Observable<any> {
    return this.http.put(`${this.apiUrl}/marcar-todas-leidas`, {}).pipe(
      catchError((err) => {
        console.error('Error al marcar todas leidas:', err);
        return of({ ok: true });
      })
    );
  }
}
