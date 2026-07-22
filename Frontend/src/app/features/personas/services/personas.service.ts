import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../../../environments/environment';
import { Persona } from '../models/persona.model';

@Injectable({
  providedIn: 'root',
})
export class PersonasService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/personas`;

  getPersonas(buscar?: string): Observable<Persona[]> {
    const url = buscar ? `${this.apiUrl}?buscar=${encodeURIComponent(buscar)}` : `${this.apiUrl}/`;
    return this.http.get<Persona[]>(url).pipe(
      catchError((err) => {
        console.warn('Error al consultar personas en backend:', err);
        return of([]);
      })
    );
  }

  getPersonaById(id: number): Observable<Persona | undefined> {
    return this.http.get<Persona>(`${this.apiUrl}/${id}`).pipe(
      catchError((err) => {
        console.warn(`Error al consultar persona ${id} en backend:`, err);
        return of(undefined);
      })
    );
  }

  createPersona(personaData: Partial<Persona>): Observable<Persona> {
    return this.http.post<Persona>(`${this.apiUrl}/`, personaData).pipe(
      catchError((err) => {
        console.error('Error al crear persona en backend:', err);
        throw err;
      })
    );
  }

  updatePersona(id: number, personaData: Partial<Persona>): Observable<Persona> {
    return this.http.put<Persona>(`${this.apiUrl}/${id}`, personaData).pipe(
      catchError((err) => {
        console.error(`Error al actualizar persona ${id} en backend:`, err);
        throw err;
      })
    );
  }
}
