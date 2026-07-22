import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../../../environments/environment';
import { Certificado } from '../models/certificado.model';

@Injectable({
  providedIn: 'root',
})
export class CertificadosService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/certificados`;

  getCertificados(): Observable<Certificado[]> {
    return this.http.get<Certificado[]>(`${this.apiUrl}/`).pipe(
      catchError((err) => {
        console.warn('Error backend certificados:', err);
        return of([]);
      })
    );
  }

  generarCertificado(data: Partial<Certificado>): Observable<Certificado> {
    return this.http.post<Certificado>(`${this.apiUrl}/`, data).pipe(
      catchError((err) => {
        console.error('Error backend generar certificado:', err);
        throw err;
      })
    );
  }
}
