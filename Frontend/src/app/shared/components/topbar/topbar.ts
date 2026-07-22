import { Component, EventEmitter, Output, inject, OnInit, PLATFORM_ID, ChangeDetectionStrategy, signal, computed, DestroyRef } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../../features/auth/services/auth.service';
import { PerfilService } from '../../../features/perfil/services/perfil.service';
import { TokenService } from '../../../core/services/token';
import { NotificacionesService } from '../../../features/notificaciones/services/notificaciones.service';

@Component({
  selector: 'app-topbar',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './topbar.html',
  styleUrl: './topbar.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TopbarComponent implements OnInit {

  @Output() menuClick = new EventEmitter<void>();

  private platformId = inject(PLATFORM_ID);
  private authService = inject(AuthService);
  private perfilService = inject(PerfilService);
  private tokenService = inject(TokenService);
  private notifService = inject(NotificacionesService);
  private router = inject(Router);
  private destroyRef = inject(DestroyRef);

  session = this.tokenService.getUserData();
  perfil = signal<any>(null);
  usuario = signal<any>(null);
  unreadNotifCount = signal<number>(0);

  fullName = computed(() => {
    const p = this.perfil();
    if (!p) return 'Usuario';
    const nombreCompleto = `${p.primer_nombre ?? ''} ${p.primer_apellido ?? ''}`.trim();
    if (nombreCompleto) return nombreCompleto;
    const u = this.usuario();
    return p.correo ?? u?.correo ?? 'Usuario';
  });

  role = computed(() => {
    return this.session?.roles?.[0] ?? 'Usuario';
  });

  initial = computed(() => {
    const p = this.perfil();
    return p?.primer_nombre?.charAt(0)?.toUpperCase() || 'U';
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
        console.error('Error cargando perfil en topbar:', err);
        this.perfil.set({});
      },
    });

    this.perfilService.getMe().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (u) => {
        this.usuario.set(u);
      },
      error: (err) => console.error('Error cargando usuario en topbar:', err),
    });

    this.cargarNotificaciones();
  }

  cargarNotificaciones(): void {
    this.notifService.getNotificaciones().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (list) => {
        if (Array.isArray(list)) {
          this.unreadNotifCount.set(list.filter((n) => !n.leida).length);
        }
      },
      error: () => this.unreadNotifCount.set(0),
    });
  }

  irANotificaciones(): void {
    this.router.navigate(['/app/notificaciones']);
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/auth/login']);
  }
}