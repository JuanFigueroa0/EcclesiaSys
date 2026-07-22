import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../../../environments/environment';
import { Pago } from '../models/pago.model';

@Injectable({
  providedIn: 'root',
})
export class PagosService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/pagos`;

  getPagos(): Observable<Pago[]> {
    return this.http.get<Pago[]>(`${this.apiUrl}/`).pipe(
      catchError((err) => {
        console.warn('Error backend pagos:', err);
        return of([]);
      })
    );
  }

  registrarPago(data: Partial<Pago>): Observable<Pago> {
    return this.http.post<Pago>(`${this.apiUrl}/`, data).pipe(
      catchError((err) => {
        console.error('Error backend registrar pago:', err);
        throw err;
      })
    );
  }
}
