import { Component, OnInit, inject, signal, computed, ChangeDetectionStrategy, DestroyRef } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { SolicitudesService } from '../../../../core/services/solicitudes';
import { SacramentosService } from '../../../../core/services/sacramentos';
import { PersonasService } from '../../../personas/services/personas.service';
import { UsuariosService } from '../../../../core/services/usuarios';
import { CertificadosService } from '../../../certificados/services/certificados.service';
import { NotificacionesService } from '../../../notificaciones/services/notificaciones.service';
import { EventosService } from '../../../eventos/services/eventos.service';
import { TokenService } from '../../../../core/services/token';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DashboardComponent implements OnInit {
  private solService = inject(SolicitudesService);
  private sacService = inject(SacramentosService);
  private personasService = inject(PersonasService);
  private usuariosService = inject(UsuariosService);
  private certService = inject(CertificadosService);
  private notifService = inject(NotificacionesService);
  private eventosService = inject(EventosService);
  private tokenService = inject(TokenService);
  private destroyRef = inject(DestroyRef);

  cargando = signal<boolean>(true);
  session = signal<any>(this.tokenService.getUserData());

  esAdmin = computed(() => {
    const roles: string[] = this.session()?.roles ?? [];
    const rolesAdmin = ['superadmin', 'administrador parroquial', 'secretario', 'párroco', 'parroco'];
    return roles.some((r) => rolesAdmin.includes(r.toLowerCase().trim()));
  });

  rolPrincipal = computed(() => {
    const roles: string[] = this.session()?.roles ?? [];
    if (roles.length === 0) return 'Usuario Fiel';
    const prioridad = ['superadmin', 'admin del sitio', 'administrador parroquial', 'párroco', 'parroco', 'secretario', 'secretaria', 'catequista'];
    for (const prio of prioridad) {
      const encontrado = roles.find((r) => r.toLowerCase().trim() === prio);
      if (encontrado) return encontrado;
    }
    const esp = roles.find((r) => !['usuario', 'usuario fiel'].includes(r.toLowerCase().trim()));
    return esp || roles[0] || 'Usuario Fiel';
  });

  stats = signal<any[]>([]);
  recentRequests = signal<any[]>([]);

  ngOnInit(): void {
    this.cargarDatos();
  }

  cargarDatos(): void {
    this.cargando.set(true);

    if (this.esAdmin()) {
      // Configuración de métricas para ADMINISTRADORES
      this.stats.set([
        { title: 'Solicitudes activas', value: 0, icon: 'bi-file-earmark-text', color: 'primary' },
        { title: 'Sacramentos', value: 0, icon: 'bi-journal-bookmark', color: 'success' },
        { title: 'Personas registradas', value: 0, icon: 'bi-people', color: 'warning' },
        { title: 'Usuarios', value: 0, icon: 'bi-person-badge', color: 'danger' },
      ]);

      this.solService.getAll().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
        next: (res) => {
          const arr = Array.isArray(res) ? res : (res as any)?.items || [];
          const count = arr.length;
          this.recentRequests.set(arr.slice(0, 5));
          this.updateStatValue(0, count);
        },
        error: () => {
          this.recentRequests.set([]);
          this.updateStatValue(0, 0);
        },
      });

      this.sacService.getAll().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
        next: (res) => {
          const arr = Array.isArray(res) ? res : (res as any)?.items || [];
          this.updateStatValue(1, arr.length);
        },
        error: () => this.updateStatValue(1, 0),
      });

      this.personasService.getPersonas().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
        next: (res) => {
          const arr = Array.isArray(res) ? res : (res as any)?.items || [];
          this.updateStatValue(2, arr.length);
        },
        error: () => this.updateStatValue(2, 0),
      });

      this.usuariosService.getAll().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
        next: (res) => {
          const arr = Array.isArray(res) ? res : (res as any)?.items || [];
          this.updateStatValue(3, arr.length);
        },
        error: () => this.updateStatValue(3, 0),
      });

    } else {
      // Configuración de métricas para USUARIOS FIELES (Estándar)
      this.stats.set([
        { title: 'Mis Solicitudes Activas', value: 0, icon: 'bi-file-earmark-text', color: 'primary' },
        { title: 'Mis Certificados', value: 0, icon: 'bi-patch-check', color: 'success' },
        { title: 'Mis Notificaciones', value: 0, icon: 'bi-bell', color: 'warning' },
        { title: 'Eventos Parroquiales', value: 0, icon: 'bi-calendar3', color: 'danger' },
      ]);

      this.solService.getMisSolicitudes().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
        next: (res) => {
          const arr = Array.isArray(res) ? res : (res as any)?.items || [];
          const count = arr.filter((s: any) => s.estado === 'Pendiente' || s.estado === 'pendiente' || s.estado === 'en_revision').length || arr.length;
          this.recentRequests.set(arr.slice(0, 5));
          this.updateStatValue(0, count);
        },
        error: () => {
          this.recentRequests.set([]);
          this.updateStatValue(0, 0);
        },
      });

      this.certService.getCertificados().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
        next: (res) => {
          const arr = Array.isArray(res) ? res : (res as any)?.items || [];
          this.updateStatValue(1, arr.length);
        },
        error: () => this.updateStatValue(1, 0),
      });

      this.notifService.getNotificaciones().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
        next: (res) => {
          const arr = Array.isArray(res) ? res : (res as any)?.items || [];
          const unread = arr.filter((n: any) => !n.leida).length;
          this.updateStatValue(2, unread);
        },
        error: () => this.updateStatValue(2, 0),
      });

      this.eventosService.getEventos().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
        next: (res) => {
          const arr = Array.isArray(res) ? res : (res as any)?.items || [];
          this.updateStatValue(3, arr.length);
        },
        error: () => this.updateStatValue(3, 0),
      });
    }

    this.cargando.set(false);
  }

  private updateStatValue(index: number, val: number): void {
    this.stats.update((currentStats) => {
      const copy = [...currentStats];
      if (copy[index]) {
        copy[index] = { ...copy[index], value: val };
      }
      return copy;
    });
  }
}