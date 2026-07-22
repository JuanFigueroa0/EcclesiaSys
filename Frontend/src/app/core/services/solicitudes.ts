import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class SolicitudesService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  getAll(): Observable<any[]> {
    return this.http.get<any>(`${this.apiUrl}/solicitudes/admin/todas`).pipe(
      map((res) => {
        const rawItems = res?.items || (Array.isArray(res) ? res : []);
        return rawItems.map((s: any) => ({
          id: s.id,
          fiel: s.persona_nombre || s.usuario_correo || `Solicitud #${s.id}`,
          sacramento: s.sacramento_nombre || `Sacramento #${s.sacramento_id}`,
          sacramento_id: s.sacramento_id,
          estado: s.estado === 'pendiente' ? 'Pendiente' : s.estado === 'aprobada' ? 'Aprobada' : s.estado === 'rechazada' ? 'Rechazada' : s.estado || 'Pendiente',
          fecha: s.created_at ? s.created_at.split('T')[0] : '',
        }));
      }),
      catchError(() => this.getMisSolicitudes())
    );
  }

  getMisSolicitudes(): Observable<any[]> {
    return this.http.get<any>(`${this.apiUrl}/solicitudes/mis-solicitudes`).pipe(
      map((res) => {
        const rawItems = res?.items || (Array.isArray(res) ? res : []);
        return rawItems.map((s: any) => ({
          id: s.id,
          fiel: s.persona_nombre || s.usuario_correo || 'Mis Trámites',
          sacramento: s.sacramento_nombre || `Sacramento #${s.sacramento_id}`,
          sacramento_id: s.sacramento_id,
          estado: s.estado === 'pendiente' ? 'Pendiente' : s.estado === 'aprobada' ? 'Aprobada' : s.estado === 'rechazada' ? 'Rechazada' : s.estado || 'Pendiente',
          fecha: s.created_at ? s.created_at.split('T')[0] : '',
        }));
      }),
      catchError((err) => {
        console.warn('Error backend mis-solicitudes:', err);
        return of([]);
      })
    );
  }

  create(payload: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/solicitudes/`, payload);
  }

  subirDocumento(
    solicitudId: number,
    file: File,
    tipoDocumento: string,
    categoria: string = 'requisito',
    personaId?: number,
    descripcion?: string
  ): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('tipo_documento', tipoDocumento);
    formData.append('categoria', categoria);
    if (personaId) formData.append('persona_id', personaId.toString());
    if (descripcion) formData.append('descripcion', descripcion);

    return this.http.post<any>(`${this.apiUrl}/solicitudes/${solicitudId}/documentos`, formData);
  }

  update(id: number, payload: { estado: string; observaciones_secretario?: string }): Observable<any> {
    const body = {
      estado: payload.estado.toLowerCase(),
      observaciones_secretario: payload.observaciones_secretario || 'Actualización de estado',
    };
    return this.http.patch<any>(`${this.apiUrl}/solicitudes/${id}/estado`, body);
  }
}