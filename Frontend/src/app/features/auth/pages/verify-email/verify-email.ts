import {
  Component,
  OnInit,
  PLATFORM_ID,
  inject,
  signal,
} from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { Title } from '@angular/platform-browser';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { take } from 'rxjs';

import { AuthService } from '../../services/auth.service';

type EstadoVerificacion = 'verificando' | 'exito' | 'error' | 'manual';

interface VerificacionExitosaGuardada {
  mensaje: string;
  esReactivacion: boolean;
}

@Component({
  selector: 'app-verify-email',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './verify-email.html',
  styleUrl: './verify-email.scss',
})
export class VerifyEmailComponent implements OnInit {
  private static readonly VERIFICACION_EXITOSA_KEY =
    'ecclesia:verify-email:exito';

  private readonly route = inject(ActivatedRoute);
  private readonly authService = inject(AuthService);
  private readonly fb = inject(FormBuilder);
  private readonly titleService = inject(Title);
  private readonly platformId = inject(PLATFORM_ID);

  private verificacionAutomaticaIniciada = false;

  readonly estado = signal<EstadoVerificacion>('verificando');
  readonly mensaje = signal('');
  readonly error = signal('');
  readonly errorReenvio = signal('');
  readonly exitoReenvio = signal('');
  readonly cargandoReenvio = signal(false);
  readonly cargandoManual = signal(false);
  readonly esReactivacion = signal(false);

  readonly manualForm = this.fb.nonNullable.group({
    token: ['', [Validators.required]],
  });

  readonly resendForm = this.fb.nonNullable.group({
    correo: ['', [Validators.required, Validators.email]],
  });

  private extraerMensajeError(err: any, fallback: string): string {
    const detail = err?.error?.detail;

    if (typeof detail === 'string') {
      return detail;
    }

    if (Array.isArray(detail) && detail.length > 0) {
      return detail.map((d) => d.msg).join(', ');
    }

    return fallback;
  }

  private esTokenYaUtilizado(mensaje: string): boolean {
    return /ya ha sido usado|ya fue utilizado|invalid.*used/i.test(mensaje);
  }

  private restaurarExitoGuardado(): boolean {
    if (!isPlatformBrowser(this.platformId)) {
      return false;
    }

    const guardado = sessionStorage.getItem(
      VerifyEmailComponent.VERIFICACION_EXITOSA_KEY
    );
    if (!guardado) {
      return false;
    }

    try {
      const data = JSON.parse(guardado) as VerificacionExitosaGuardada;
      this.esReactivacion.set(data.esReactivacion);
      this.estado.set('exito');
      this.mensaje.set(data.mensaje);
      return true;
    } catch {
      sessionStorage.removeItem(VerifyEmailComponent.VERIFICACION_EXITOSA_KEY);
      return false;
    }
  }

  private marcarExito(mensaje: string): void {
    this.estado.set('exito');
    this.mensaje.set(mensaje);

    if (isPlatformBrowser(this.platformId)) {
      sessionStorage.setItem(
        VerifyEmailComponent.VERIFICACION_EXITOSA_KEY,
        JSON.stringify({
          mensaje,
          esReactivacion: this.esReactivacion(),
        } satisfies VerificacionExitosaGuardada)
      );
    }
  }

  ngOnInit(): void {
    const params = this.route.snapshot.queryParamMap;
    const token = params.get('token');
    const correoParam = params.get('correo');
    const tipo = params.get('tipo');

    this.esReactivacion.set(tipo === 'reactivacion');
    if (correoParam) {
      this.resendForm.patchValue({ correo: correoParam });
    }

    this.titleService.setTitle(
      `EcclesiaSys – ${this.esReactivacion() ? 'Reactivación de cuenta' : 'Verificar correo'}`
    );

    if (token) {
      if (isPlatformBrowser(this.platformId)) {
        this.verificarConToken(token);
      }
      return;
    }

    if (this.restaurarExitoGuardado()) {
      return;
    }

    this.estado.set('manual');
  }

  private verificarConToken(token: string): void {
    if (this.verificacionAutomaticaIniciada || this.estado() === 'exito') {
      return;
    }
    this.verificacionAutomaticaIniciada = true;

    this.authService
      .verifyEmailManual({ token })
      .pipe(take(1))
      .subscribe({
        next: (r) => {
          this.marcarExito(
            r.mensaje ??
              (this.esReactivacion()
                ? '¡Tu cuenta ha sido reactivada exitosamente!'
                : '¡Correo verificado exitosamente!')
          );
        },
        error: (err) => {
          if (this.estado() === 'exito') {
            return;
          }

          const mensajeError = this.extraerMensajeError(
            err,
            'El enlace es inválido o ya expiró.'
          );

          if (this.esTokenYaUtilizado(mensajeError)) {
            this.marcarExito(
              this.esReactivacion()
                ? 'Tu cuenta ya fue reactivada. Ya puedes iniciar sesión.'
                : 'Tu correo ya fue verificado. Ya puedes iniciar sesión.'
            );
            return;
          }

          this.estado.set('error');
          this.error.set(mensajeError);
        },
      });
  }

  onSubmitManual(): void {
    const token = this.manualForm.getRawValue().token.trim();
    if (!token) {
      this.error.set('Debes ingresar el código.');
      return;
    }
    this.error.set('');
    this.cargandoManual.set(true);

    this.authService
      .verifyEmailManual({ token })
      .pipe(take(1))
      .subscribe({
        next: (r) => {
          this.cargandoManual.set(false);
          this.marcarExito(r.mensaje ?? '¡Correo verificado exitosamente!');
        },
        error: (err) => {
          this.cargandoManual.set(false);
          this.error.set(
            this.extraerMensajeError(err, 'No se pudo verificar el código.')
          );
        },
      });
  }

  onReenviar(): void {
    const correo = this.resendForm.getRawValue().correo.trim();
    if (!correo) {
      this.errorReenvio.set('Debes ingresar tu correo.');
      return;
    }
    this.errorReenvio.set('');
    this.exitoReenvio.set('');
    this.cargandoReenvio.set(true);

    this.authService
      .resendVerificationEmail({ correo })
      .pipe(take(1))
      .subscribe({
        next: (r) => {
          this.cargandoReenvio.set(false);
          this.exitoReenvio.set(r.mensaje ?? 'Correo reenviado exitosamente.');
        },
        error: (err) => {
          this.cargandoReenvio.set(false);
          this.errorReenvio.set(
            this.extraerMensajeError(err, 'No se pudo reenviar el correo.')
          );
        },
      });
  }
}
