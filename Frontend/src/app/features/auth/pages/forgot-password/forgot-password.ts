import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [CommonModule, RouterLink, ReactiveFormsModule],
  templateUrl: './forgot-password.html',
  styleUrl: './forgot-password.scss',
})
export class ForgotPasswordComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);

  cargando = false;
  mensajeExito = '';
  mensajeError = '';

  form: FormGroup = this.fb.group({
    correo: ['', [Validators.required, Validators.email]],
  });

  enviarSolicitud(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.cargando = true;
    this.mensajeExito = '';
    this.mensajeError = '';

    const correo = this.form.value.correo;

    this.authService.recuperarContrasena(correo).subscribe({
      next: () => {
        this.cargando = false;
        this.mensajeExito = `Hemos enviado las instrucciones para restablecer tu contraseña al correo ${correo}.`;
        this.form.reset();
      },
      error: (err) => {
        this.cargando = false;
        // Si el backend responde o falla por red, damos confirmación clara al usuario
        this.mensajeExito = `Si el correo ${correo} se encuentra registrado, recibirás un enlace de recuperación.`;
      },
    });
  }
}
