import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-reset-password',
  standalone: true,
  imports: [CommonModule, RouterLink, ReactiveFormsModule],
  templateUrl: './reset-password.html',
  styleUrl: './reset-password.scss',
})
export class ResetPasswordComponent implements OnInit {
  private fb = inject(FormBuilder);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private authService = inject(AuthService);

  token = '';
  cargando = false;
  mensajeExito = '';
  mensajeError = '';

  form: FormGroup = this.fb.group({
    contrasena_nueva: ['', [Validators.required, Validators.minLength(6)]],
    confirmar_contrasena: ['', [Validators.required]],
  });

  ngOnInit(): void {
    this.token = this.route.snapshot.queryParams['token'] || '';
  }

  restablecer(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const { contrasena_nueva, confirmar_contrasena } = this.form.value;
    if (contrasena_nueva !== confirmar_contrasena) {
      this.mensajeError = 'Las contraseñas no coinciden.';
      return;
    }

    this.cargando = true;
    this.mensajeError = '';
    this.mensajeExito = '';

    this.authService.restablecerContrasena(this.token, contrasena_nueva).subscribe({
      next: () => {
        this.cargando = false;
        this.mensajeExito = 'Tu contraseña ha sido actualizada con éxito. Redirigiendo al inicio de sesión...';
        setTimeout(() => this.router.navigate(['/auth/login']), 2500);
      },
      error: (err) => {
        this.cargando = false;
        this.mensajeError = err?.error?.detail || 'No se pudo restablecer la contraseña. El token puede ser inválido o haber expirado.';
      },
    });
  }
}
