import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { Chatbot } from '../../../../shared/components/chatbot/chatbot';

import { AuthService } from '../../../../core/services/auth';
import { PerfilService } from '../../../perfil/services/perfil.service';

@Component({
  selector: 'app-login',
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterLink,
    Chatbot
  ],
  templateUrl: './login.html',
  styleUrl: './login.scss',
})
export class LoginComponent {

  private router = inject(Router);
  private authService = inject(AuthService);
  private perfilService = inject(PerfilService);
  private fb = inject(FormBuilder);

  showPassword = false;
  loading = false;
  errorMessage = '';

  loginForm: FormGroup = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', Validators.required],
  });

  togglePassword(): void {
    this.showPassword = !this.showPassword;
  }

  onSubmit(): void {
    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      this.errorMessage = 'Debes ingresar tu correo y contraseña.';
      return;
    }

    this.loading = true;
    this.errorMessage = '';

    const { email, password } = this.loginForm.value;

    this.authService.login({
      correo: email,
      contrasena: password,
    })
    .subscribe({
      next: (response) => {
        if (response.estado === 'INACTIVO') {
          this.errorMessage = 'La cuenta se encuentra inactiva.';
          this.loading = false;
          return;
        }

        this.loading = false;
        this.router.navigate(['/app/dashboard']);
      },
      error: (error) => {
        this.loading = false;
        const backendMessage = error?.error?.message;

        switch (backendMessage) {
          case 'CUENTA_INACTIVA':
            this.errorMessage = 'Tu cuenta está inactiva.';
            break;
          case 'CUENTA_ELIMINADA':
            this.errorMessage = 'Tu cuenta fue eliminada.';
            break;
          case 'CREDENCIALES_INVALIDAS':
            this.errorMessage = 'Correo o contraseña incorrectos.';
            break;
          default:
            this.errorMessage = 'No fue posible iniciar sesión.';
        }
      }
    });
  }
}