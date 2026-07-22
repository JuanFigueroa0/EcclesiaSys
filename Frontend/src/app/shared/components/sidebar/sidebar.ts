import {
  Component,
  EventEmitter,
  Input,
  Output,
  inject,
  OnInit,
  PLATFORM_ID,
  ChangeDetectionStrategy,
  signal,
  computed,
  DestroyRef,
} from '@angular/core';

import {
  RouterLink,
  RouterLinkActive,
} from '@angular/router';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

import { TokenService } from '../../../core/services/token';
import { PerfilService } from '../../../features/perfil/services/perfil.service';
import { SolicitudesService } from '../../../core/services/solicitudes';
import { NotificacionesService } from '../../../features/notificaciones/services/notificaciones.service';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
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
  private destroyRef = inject(DestroyRef);

  session = this.tokenService.getUserData();
  perfil = signal<any>(null);
  usuario = signal<any>(null);
  solicitudesCount = signal<number>(0);
  notificacionesCount = signal<number>(0);

  userRoles = computed(() => {
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
  });

  fullName = computed(() => {
    const p = this.perfil();
    if (!p) return 'Cargando...';
    const nombreCompleto = `${p.primer_nombre ?? ''} ${p.primer_apellido ?? ''}`.trim();
    if (nombreCompleto) return nombreCompleto;
    const u = this.usuario();
    return p.correo ?? u?.correo ?? 'Usuario';
  });

  role = computed(() => {
    return this.session?.roles?.[0] ?? 'Usuario Fiel';
  });

  initials = computed(() => {
    const p = this.perfil();
    if (!p?.primer_nombre) return 'US';
    return (
      p.primer_nombre.charAt(0) +
      (p.primer_apellido?.charAt(0) ?? '')
    ).toUpperCase();
  });

  tieneSeccionGestion = computed(() => true);

  tieneSeccionAdministracion = computed(() => {
    return this.tieneRol(['Superadmin', 'Administrador Parroquial']);
  });

  ngOnInit(): void {
    if (!isPlatformBrowser(this.platformId) || !this.tokenService.isLoggedIn()) {
      return;
    }

    this.perfilService.getPerfil().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (p) => {
        this.perfil.set(p);
      },
      error: (err) => {
        console.error('Error cargando perfil en sidebar:', err);
        this.perfil.set({});
      },
    });

    this.perfilService.getMe().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (u) => {
        this.usuario.set(u);
      },
      error: (err) => console.error('Error cargando usuario en sidebar:', err),
    });

    this.cargarIndicadoresReales();
  }

  cargarIndicadoresReales(): void {
    const esAdmin = this.tieneRol(['Superadmin', 'Administrador Parroquial', 'Secretario', 'Párroco']);
    const solObs = esAdmin ? this.solService.getAll() : this.solService.getMisSolicitudes();

    solObs.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (list) => {
        if (Array.isArray(list)) {
          this.solicitudesCount.set(list.filter(
            (s: any) => s.estado === 'Pendiente' || s.estado === 'pendiente' || s.estado === 'en_revision'
          ).length);
        } else {
          this.solicitudesCount.set(0);
        }
      },
      error: () => this.solicitudesCount.set(0),
    });

    this.notifService.getNotificaciones().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (list) => {
        if (Array.isArray(list)) {
          this.notificacionesCount.set(list.filter((n) => !n.leida).length);
        } else {
          this.notificacionesCount.set(0);
        }
      },
      error: () => this.notificacionesCount.set(0),
    });
  }

  tieneRol(rolesPermitidos: string[]): boolean {
    if (!rolesPermitidos || rolesPermitidos.length === 0) return true;

    const misRoles = this.userRoles();
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

  closeOnMobile(): void {
    if (window.innerWidth <= 991) {
      this.closeMobile.emit();
    }
  }
}