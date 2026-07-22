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
import { isPlatformBrowser, CommonModule } from '@angular/common';

import { TokenService } from '../../../core/services/token';
import { PerfilService } from '../../../features/perfil/services/perfil.service';
import { SolicitudesService } from '../../../core/services/solicitudes';
import { NotificacionesService } from '../../../features/notificaciones/services/notificaciones.service';

@Component({
  selector: 'app-sidebar',
  imports: [CommonModule, RouterLink, RouterLinkActive],
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
  private solService = inject(SolicitudesService);
  private notifService = inject(NotificacionesService);

  session = this.tokenService.getUserData();
  perfil: any = null;
  usuario: any = null;
  solicitudesCount = 0;
  notificacionesCount = 0;

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

    this.cargarIndicadoresReales();
  }

  cargarIndicadoresReales(): void {
    const esAdmin = this.tieneRol(['Superadmin', 'Administrador Parroquial', 'Secretario', 'Párroco']);
    const solObs = esAdmin ? this.solService.getAll() : this.solService.getMisSolicitudes();

    solObs.subscribe({
      next: (list) => {
        if (Array.isArray(list)) {
          this.solicitudesCount = list.filter(
            (s: any) => s.estado === 'Pendiente' || s.estado === 'pendiente' || s.estado === 'en_revision'
          ).length;
        } else {
          this.solicitudesCount = 0;
        }
      },
      error: () => (this.solicitudesCount = 0),
    });

    this.notifService.getNotificaciones().subscribe({
      next: (list) => {
        if (Array.isArray(list)) {
          this.notificacionesCount = list.filter((n) => !n.leida).length;
        } else {
          this.notificacionesCount = 0;
        }
      },
      error: () => (this.notificacionesCount = 0),
    });
  }

  get userRoles(): string[] {
    const session = this.tokenService.getUserData();
    const rawRoles: string[] = session?.roles ?? [];
    return rawRoles.map((r) =>
      r
        .toLowerCase()
        .trim()
        .replace(/[áäâ]/g, 'a')
        .replace(/[óöô]/g, 'o')
        .replace(/[úüû]/g, 'u')
        .replace(/[éëê]/g, 'e')
        .replace(/[íïî]/g, 'i')
    );
  }

  tieneRol(rolesPermitidos: string[]): boolean {
    if (!rolesPermitidos || rolesPermitidos.length === 0) return true;

    const misRoles = this.userRoles;
    return rolesPermitidos.some((allowed) => {
      const normAllowed = allowed
        .toLowerCase()
        .trim()
        .replace(/[áäâ]/g, 'a')
        .replace(/[óöô]/g, 'o')
        .replace(/[úüû]/g, 'u')
        .replace(/[éëê]/g, 'e')
        .replace(/[íïî]/g, 'i');

      return misRoles.some((userRole) => userRole.includes(normAllowed) || normAllowed.includes(userRole));
    });
  }

  get tieneSeccionGestion(): boolean {
    return true;
  }

  get tieneSeccionAdministracion(): boolean {
    return this.tieneRol(['Superadmin', 'Administrador Parroquial']);
  }

  get fullName(): string {
    if (!this.perfil) return 'Cargando...';

    const nombreCompleto = `${this.perfil.primer_nombre ?? ''} ${this.perfil.primer_apellido ?? ''}`.trim();

    if (nombreCompleto) {
      return nombreCompleto;
    }

    return this.perfil.correo ?? this.usuario?.correo ?? 'Usuario';
  }

  get role(): string {
    return this.session?.roles?.[0] ?? 'Usuario Fiel';
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