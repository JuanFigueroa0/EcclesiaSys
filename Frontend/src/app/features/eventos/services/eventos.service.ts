import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../../../environments/environment';
import { Evento } from '../models/evento.model';

@Injectable({
  providedIn: 'root',
})
export class EventosService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/eventos`;

  getEventos(): Observable<Evento[]> {
    return this.http.get<Evento[]>(`${this.apiUrl}/`).pipe(
      catchError((err) => {
        console.warn('Error backend eventos:', err);
        return of([]);
      })
    );
  }

  createEvento(data: Partial<Evento>): Observable<Evento> {
    return this.http.post<Evento>(`${this.apiUrl}/`, data).pipe(
      catchError((err) => {
        console.error('Error backend crear evento:', err);
        throw err;
      })
    );
  }
}
