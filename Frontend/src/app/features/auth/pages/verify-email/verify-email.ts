import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../../environments/environment';

@Component({
  selector: 'app-verify-email',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './verify-email.html',
  styleUrl: './verify-email.scss',
})
export class VerifyEmailComponent implements OnInit {
  private router = inject(Router);
  private http = inject(HttpClient);
  private route = inject(ActivatedRoute);

  loading = true;
  errorMessage = '';
  successMessage = '';
  token: string | null = null;

  ngOnInit(): void {
    // Obtener token del query parameter
    this.route.queryParams.subscribe(params => {
      this.token = params['token'] || null;
      
      if (this.token) {
        this.verifyEmail();
      } else {
        this.loading = false;
        this.errorMessage = 'Token de verificación no encontrado.';
      }
    });
  }

  private verifyEmail(): void {
    // Aquí iría la lógica para verificar correo
    // POST a /auth/verify-email con token
    this.loading = false;
    this.successMessage = 'Correo verificado exitosamente. Redirigiendo...';
    
    setTimeout(() => {
      this.router.navigate(['/auth/login']);
    }, 2000);
  }
}