import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../../../environments/environment';
import { Curso } from '../models/curso.model';

@Injectable({
  providedIn: 'root',
})
export class CursosService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/cursos`;

  getCursos(): Observable<Curso[]> {
    return this.http.get<Curso[]>(`${this.apiUrl}/`).pipe(
      catchError((err) => {
        console.warn('Error backend cursos:', err);
        return of([]);
      })
    );
  }

  crearCurso(data: Partial<Curso>): Observable<Curso> {
    return this.http.post<Curso>(`${this.apiUrl}/`, data).pipe(
      catchError((err) => {
        console.error('Error backend crear curso:', err);
        throw err;
      })
    );
  }
}
