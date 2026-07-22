import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class UsuariosService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  getAll(): Observable<any[]> {
    return this.http.get<any>(`${this.apiUrl}/usuarios/admin/list`).pipe(
      map((res) => {
        if (res && res.items) {
          return res.items.map((u: any) => {
            const rolesList: string[] = (u.roles || []).map((r: any) => (typeof r === 'string' ? r : r?.nombre || ''));
            const prioridad = ['superadmin', 'admin del sitio', 'administrador parroquial', 'párroco', 'parroco', 'secretario', 'secretaria', 'catequista'];
            let rolPrincipal = 'Usuario Fiel';
            let rolId = u.roles?.[0]?.id || null;

            for (const prio of prioridad) {
              const rObj = (u.roles || []).find((r: any) => (typeof r === 'string' ? r : r?.nombre || '').toLowerCase().trim() === prio);
              if (rObj) {
                rolPrincipal = typeof rObj === 'string' ? rObj : rObj.nombre;
                rolId = typeof rObj === 'string' ? null : rObj.id;
                break;
              }
            }

            if (rolPrincipal === 'Usuario Fiel' && rolesList.length > 0) {
              const rObj = (u.roles || []).find((r: any) => !['usuario', 'usuario fiel'].includes((typeof r === 'string' ? r : r?.nombre || '').toLowerCase().trim()));
              if (rObj) {
                rolPrincipal = typeof rObj === 'string' ? rObj : rObj.nombre;
                rolId = typeof rObj === 'string' ? null : rObj.id;
              } else {
                rolPrincipal = typeof u.roles[0] === 'string' ? u.roles[0] : u.roles[0]?.nombre || 'Usuario Fiel';
              }
            }

            return {
              id: u.id,
              nombre: u.correo ? u.correo.split('@')[0] : 'Usuario',
              correo: u.correo,
              rol: rolPrincipal,
              rol_id: rolId,
              estado: u.estado === 'activo' || u.estado === 'Activo' ? 'Activo' : 'Inactivo',
            };
          });
        }
        return Array.isArray(res) ? res : [];
      }),
      catchError((err) => {
        console.warn('Error al listar usuarios admin:', err);
        return of([]);
      })
    );
  }

  getById(id: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/usuarios/admin/${id}`).pipe(
      catchError((err) => {
        console.warn(`Error al obtener usuario admin ${id}:`, err);
        return of(null);
      })
    );
  }

  create(payload: { correo: string; contrasena: string }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/auth/register`, payload);
  }

  cambiarEstado(usuarioId: number, estado: string): Observable<any> {
    return this.http.patch<any>(`${this.apiUrl}/usuarios/admin/${usuarioId}/estado?estado=${encodeURIComponent(estado)}`, {});
  }

  delete(id: number): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/usuarios/admin/${id}`);
  }
}