import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../../../environments/environment';
import { ConfiguracionParroquial } from '../models/configuracion.model';

@Injectable({
  providedIn: 'root',
})
export class ConfiguracionService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/configuracion`;

  getConfiguracion(): Observable<ConfiguracionParroquial> {
    return this.http.get<ConfiguracionParroquial>(`${this.apiUrl}/`).pipe(
      catchError((err) => {
        console.warn('Error backend configuración:', err);
        return of({
          nombre_parroquia: '',
          direccion: '',
          telefono: '',
          email_parroquia: '',
          parroco_actual: '',
          plantilla_activa: 'clasica',
          incluir_qr: true,
          incluir_sello: true,
          dias_retencion_docs: 1825,
          notif_email: true,
          notif_telegram: false,
          telegram_bot_token: '',
        });
      })
    );
  }

  updateConfiguracion(data: Partial<ConfiguracionParroquial>): Observable<ConfiguracionParroquial> {
    return this.http.put<ConfiguracionParroquial>(`${this.apiUrl}/`, data).pipe(
      catchError((err) => {
        console.error('Error backend guardar configuración:', err);
        throw err;
      })
    );
  }
}
