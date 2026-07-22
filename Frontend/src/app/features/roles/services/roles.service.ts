import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../../../environments/environment';
import { Rol } from '../models/rol.model';

@Injectable({
  providedIn: 'root',
})
export class RolesService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/roles`;

  obtenerRoles(): Observable<Rol[]> {
    return this.http.get<Rol[]>(`${this.apiUrl}/`).pipe(
      catchError((err) => {
        console.warn('Error backend roles:', err);
        return of([]);
      })
    );
  }

  crearRol(rolData: Partial<Rol>): Observable<Rol> {
    return this.http.post<Rol>(`${this.apiUrl}/`, rolData).pipe(
      catchError((err) => {
        console.error('Error backend crear rol:', err);
        throw err;
      })
    );
  }

  actualizarRol(id: number, rolData: Partial<Rol>): Observable<Rol> {
    return this.http.put<Rol>(`${this.apiUrl}/${id}`, rolData).pipe(
      catchError((err) => {
        console.error(`Error backend actualizar rol ${id}:`, err);
        throw err;
      })
    );
  }

  asignarRolAUsuario(usuario_id: number, rol_id: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/asignar-usuario`, {
      usuario_id,
      rol_id,
    });
  }

  removerRolDeUsuario(usuario_id: number, rol_id: number): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/remover-usuario/${usuario_id}/${rol_id}`);
  }
}