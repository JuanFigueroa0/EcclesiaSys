import { Component, EventEmitter, Output, inject, OnInit, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from '../../../features/auth/services/auth.service';
import { PerfilService } from '../../../features/perfil/services/perfil.service';
import { TokenService } from '../../../core/services/token';

@Component({
  selector: 'app-topbar',
  imports: [CommonModule],
  templateUrl: './topbar.html',
  styleUrl: './topbar.scss',
})
export class TopbarComponent implements OnInit {

  @Output() menuClick = new EventEmitter<void>();

  private platformId = inject(PLATFORM_ID);
  private authService = inject(AuthService);
  private perfilService = inject(PerfilService);
  private tokenService = inject(TokenService);
  private router = inject(Router);

  session = this.tokenService.getUserData();
  perfil: any = null;
  usuario: any = null;

  ngOnInit(): void {
    if (!isPlatformBrowser(this.platformId) || !this.tokenService.isLoggedIn()) {
      return;
    }

    this.perfilService.getPerfil().subscribe({
      next: (p) => {
        this.perfil = p;
      },
      error: (err) => {
        console.error('Error cargando perfil en topbar:', err);
        this.perfil = {};
      },
    });

    this.perfilService.getMe().subscribe({
      next: (u) => {
        this.usuario = u;
      },
      error: (err) => console.error('Error cargando usuario en topbar:', err),
    });
  }

  get fullName(): string {

    if (!this.perfil) return 'Usuario';

    const nombreCompleto = `${this.perfil.primer_nombre ?? ''} ${this.perfil.primer_apellido ?? ''}`.trim();

    if (nombreCompleto) {
      return nombreCompleto;
    }

    return this.perfil.correo ?? this.usuario?.correo ?? 'Usuario';
  }

  get role(): string {
    return this.session?.roles?.[0] ?? 'Usuario';
  }

  get initial(): string {
    return this.perfil?.primer_nombre?.charAt(0)?.toUpperCase() || 'U';
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/auth/login']);
  }
}