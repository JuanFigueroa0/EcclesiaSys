import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../../../environments/environment';

export interface PermisoItem {
  id: number;
  nombre: string;
  codigo?: string;
  descripcion: string;
  modulo_id?: number;
  activo?: boolean;
}

@Injectable({
  providedIn: 'root',
})
export class PermisosService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/permisos`;

  getPermisos(): Observable<PermisoItem[]> {
    return this.http.get<PermisoItem[]>(`${this.apiUrl}/`).pipe(
      catchError((err) => {
        console.warn('Error backend al listar permisos:', err);
        return of([]);
      })
    );
  }

  getPermisosDeRol(rolId: number): Observable<PermisoItem[]> {
    return this.http.get<PermisoItem[]>(`${this.apiUrl}/rol/${rolId}`).pipe(
      catchError((err) => {
        console.warn(`Error backend al obtener permisos del rol ${rolId}:`, err);
        return of([]);
      })
    );
  }

  asignarPermisosARol(rolId: number, permisosIds: number[]): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/rol/${rolId}/asignar`, {
      permisos_ids: permisosIds,
    });
  }

  removerPermisoDeRol(rolId: number, permisoId: number): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/rol/${rolId}/permiso/${permisoId}`);
  }
}
