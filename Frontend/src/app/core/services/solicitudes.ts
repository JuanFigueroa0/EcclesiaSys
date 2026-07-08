import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class SolicitudesService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  getAll(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/solicitudes`);
  }

  create(payload: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/solicitudes`, payload);
  }

  update(id: number, payload: any): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/solicitudes/${id}`, payload);
  }
}