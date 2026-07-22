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
        return rawItems.map((s: any) => this.mapSolicitudItem(s));
      }),
      catchError(() => this.getMisSolicitudes())
    );
  }

  getMisSolicitudes(): Observable<any[]> {
    return this.http.get<any>(`${this.apiUrl}/solicitudes/mis-solicitudes`).pipe(
      map((res) => {
        const rawItems = res?.items || (Array.isArray(res) ? res : []);
        return rawItems.map((s: any) => this.mapSolicitudItem(s));
      }),
      catchError((err) => {
        console.warn('Error backend mis-solicitudes:', err);
        return of([]);
      })
    );
  }

  getById(id: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/solicitudes/${id}`).pipe(
      catchError((err) => {
        console.warn(`Error al consultar detalle de solicitud ${id}:`, err);
        return of(null);
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
      observaciones_secretario: payload.observaciones_secretario || '',
    };
    return this.http.patch<any>(`${this.apiUrl}/solicitudes/${id}/estado`, body);
  }

  private mapSolicitudItem(s: any): any {
    const rawEstado = (s.estado || 'pendiente').toLowerCase();
    const estadoLabels: Record<string, string> = {
      pendiente: 'Pendiente',
      en_revision: 'En Revisión',
      documentacion_incompleta: 'Doc. Incompleta',
      aprobada: 'Aprobada',
      rechazada: 'Rechazada',
      cancelada: 'Cancelada',
    };

    return {
      id: s.id,
      fiel: s.persona_nombre || s.usuario_correo || `Fiel Solicitante #${s.id}`,
      usuario_correo: s.usuario_correo || '',
      sacramento: s.sacramento_nombre || `Sacramento #${s.sacramento_id}`,
      sacramento_id: s.sacramento_id,
      estado: estadoLabels[rawEstado] || s.estado || 'Pendiente',
      raw_estado: rawEstado,
      fecha: s.created_at ? s.created_at.split('T')[0] : '',
      requiere_validacion_manual: s.requiere_validacion_manual,
    };
  }
}