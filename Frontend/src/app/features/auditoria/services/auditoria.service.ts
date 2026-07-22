import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../../../environments/environment';
import { AuditoriaLog } from '../models/auditoria.model';

@Injectable({
  providedIn: 'root',
})
export class AuditoriaService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/auditoria`;

  getLogs(): Observable<AuditoriaLog[]> {
    return this.http.get<AuditoriaLog[]>(`${this.apiUrl}/`).pipe(
      catchError((err) => {
        console.warn('Error backend auditoría:', err);
        return of([]);
      })
    );
  }
}
