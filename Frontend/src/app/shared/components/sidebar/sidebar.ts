import {
  Component,
  EventEmitter,
  Input,
  Output,
  inject,
  OnInit,
  PLATFORM_ID,
} from '@angular/core';

import {
  RouterLink,
  RouterLinkActive,
} from '@angular/router';
import { isPlatformBrowser } from '@angular/common';

import { TokenService } from '../../../core/services/token';
import { PerfilService } from '../../../features/perfil/services/perfil.service';

@Component({
  selector: 'app-sidebar',
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.scss',
})
export class SidebarComponent implements OnInit {

  @Input() collapsed = false;
  @Input() mobileOpen = false;

  @Output() closeMobile = new EventEmitter<void>();

  private platformId = inject(PLATFORM_ID);
  private tokenService = inject(TokenService);
  private perfilService = inject(PerfilService);

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
        console.error('Error cargando perfil en sidebar:', err);
        this.perfil = {};
      },
    });

    this.perfilService.getMe().subscribe({
      next: (u) => {
        this.usuario = u;
      },
      error: (err) => console.error('Error cargando usuario en sidebar:', err),
    });
  }

  get fullName(): string {

    if (!this.perfil) return 'Cargando...';

    const nombreCompleto = `${this.perfil.primer_nombre ?? ''} ${this.perfil.primer_apellido ?? ''}`.trim();

    if (nombreCompleto) {
      return nombreCompleto;
    }

    // Si no hay nombre/apellido, usamos el correo del perfil
    // y si tampoco existe ahí, lo tomamos del usuario (getMe())
    return this.perfil.correo ?? this.usuario?.correo ?? 'Usuario';
  }

  get role(): string {
    return this.session?.roles?.[0] ?? 'Usuario';
  }

  get initials(): string {
    if (!this.perfil?.primer_nombre) return 'US';

    return (
      this.perfil.primer_nombre.charAt(0) +
      (this.perfil.primer_apellido?.charAt(0) ?? '')
    ).toUpperCase();
  }

  closeOnMobile(): void {
    if (window.innerWidth <= 991) {
      this.closeMobile.emit();
    }
  }
}