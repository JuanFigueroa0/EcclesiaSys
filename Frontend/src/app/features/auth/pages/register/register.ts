import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { AuthService } from '../../../../core/services/auth';

interface PasswordStrength {
  esValida: boolean;
  score: number; // 0-5
  label: string;
}

@Component({
  selector: 'app-register',
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterLink
  ],
  templateUrl: './register.html',
  styleUrl: './register.scss',
})
export class RegisterComponent {

  private router = inject(Router);
  private authService = inject(AuthService);
  private fb = inject(FormBuilder);

  showPassword = false;
  showConfirm = false;

  loading = false;
  errorMessage = '';
  successMessage = '';

  cuentaEliminada = false;
  reactivando = false;
  errorReactivacion = '';
  exitoReactivacion = '';

  registerForm: FormGroup = this.fb.group(
    {
      correo: ['', [Validators.required, Validators.email]],
      contrasena: ['', [Validators.required, Validators.minLength(8)]],
      confirmar: ['', Validators.required],
    },
    { validators: this.passwordsCoincidenValidator }
  );

  togglePassword(): void {
    this.showPassword = !this.showPassword;
  }

  toggleConfirm(): void {
    this.showConfirm = !this.showConfirm;
  }

  get strength(): PasswordStrength {
    return this.calcularFuerza(this.registerForm.value.contrasena ?? '');
  }

  get noCoinciden(): boolean {
    const confirmar = this.registerForm.get('confirmar');
    return !!confirmar?.value && this.registerForm.hasError('passwordsNoCoinciden');
  }

  onSubmit(): void {
    this.errorMessage = '';
    this.successMessage = '';
    this.cuentaEliminada = false;
    this.errorReactivacion = '';
    this.exitoReactivacion = '';

    if (this.registerForm.invalid) {
      this.registerForm.markAllAsTouched();

      if (this.registerForm.hasError('passwordsNoCoinciden')) {
        this.errorMessage = 'Las contraseñas no coinciden.';
        return;
      }

      this.errorMessage = 'Completa todos los campos.';
      return;
    }

    if (!this.strength.esValida) {
      this.errorMessage =
        'La contraseña debe incluir mayúscula, minúscula, número y un carácter especial (@$!%*?&_-.)';
      return;
    }

    this.loading = true;
    this.registerForm.disable();

    const { correo, contrasena } = this.registerForm.value;

    this.authService.register({
      correo,
      contrasena,
    })
    .subscribe({
      next: () => {
        this.loading = false;
        this.successMessage = 'Cuenta creada correctamente.';
        this.registerForm.reset();
        this.registerForm.enable();
      },
      error: (error) => {
        this.loading = false;
        this.registerForm.enable();
        const detail = error?.error?.detail;

        // 422 de FastAPI: detail es un array de errores de validación
        if (Array.isArray(detail)) {
          this.errorMessage = detail[0]?.msg ?? 'Datos inválidos.';
          return;
        }

        // ⚠️ Pendiente confirmar: qué status/shape devuelve el backend
        // cuando el correo ya existe o la cuenta está inactiva.
        // Por ahora asumo que viene como string en detail.
        if (typeof detail === 'string') {
          if (detail.includes('INACTIVA') || detail.includes('inactiva')) {
            this.cuentaEliminada = true;
            return;
          }
          this.errorMessage = detail;
          return;
        }

        this.errorMessage = 'No fue posible completar el registro.';
      }
    });
  }

  onReactivar(): void {
    this.errorReactivacion = '';
    this.exitoReactivacion = '';
    this.reactivando = true;

    const correo = this.registerForm.get('correo')?.value;

    this.authService.reactivarCuenta(correo).subscribe({
      next: (response) => {
        this.reactivando = false;
        this.exitoReactivacion = response.mensaje ?? 'Cuenta reactivada. Revisa tu correo.';
      },
      error: (error) => {
        this.reactivando = false;
        this.errorReactivacion =
          error?.error?.message ?? 'Error al reactivar la cuenta.';
      }
    });
  }

  onNoCuentaEliminada(): void {
    this.cuentaEliminada = false;
    this.registerForm.reset();
  }

  private calcularFuerza(contrasena: string): PasswordStrength {
    let score = 0;
    if (contrasena.length >= 8) score++;
    if (/[A-Z]/.test(contrasena)) score++;
    if (/[a-z]/.test(contrasena)) score++;
    if (/[0-9]/.test(contrasena)) score++;
    if (/[@$!%*?&_.\-]/.test(contrasena)) score++;

    const esValida =
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_.\-])[A-Za-z\d@$!%*?&_.\-]{8,}$/.test(contrasena);

    const labels = ['Muy débil', 'Débil', 'Regular', 'Buena', 'Fuerte', 'Muy fuerte'];

    return { esValida, score, label: labels[score] };
  }

  private passwordsCoincidenValidator(group: AbstractControl): ValidationErrors | null {
    const contrasena = group.get('contrasena')?.value;
    const confirmar = group.get('confirmar')?.value;

    if (contrasena && confirmar && contrasena !== confirmar) {
      return { passwordsNoCoinciden: true };
    }

    return null;
  }
}