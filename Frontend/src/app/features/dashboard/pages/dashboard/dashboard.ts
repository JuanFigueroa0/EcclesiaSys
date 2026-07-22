import { Component, OnInit, inject } from '@angular/core';
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

  cargando = true;
  session = this.tokenService.getUserData();

  get esAdmin(): boolean {
    const roles: string[] = this.session?.roles ?? [];
    const rolesAdmin = ['superadmin', 'administrador parroquial', 'secretario', 'párroco', 'parroco'];
    return roles.some((r) => rolesAdmin.includes(r.toLowerCase().trim()));
  }

  stats: any[] = [];
  recentRequests: any[] = [];

  ngOnInit(): void {
    this.cargarDatos();
  }

  cargarDatos(): void {
    this.cargando = true;

    if (this.esAdmin) {
      // Configuración de métricas para ADMINISTRADORES
      this.stats = [
        { title: 'Solicitudes activas', value: 0, icon: 'bi-file-earmark-text', color: 'primary' },
        { title: 'Sacramentos', value: 0, icon: 'bi-journal-bookmark', color: 'success' },
        { title: 'Personas registradas', value: 0, icon: 'bi-people', color: 'warning' },
        { title: 'Usuarios', value: 0, icon: 'bi-person-badge', color: 'danger' },
      ];

      this.solService.getAll().subscribe({
        next: (list) => {
          const arr = list || [];
          this.stats[0].value = arr.filter((s: any) => s.estado === 'Pendiente' || s.estado === 'pendiente' || s.estado === 'en_revision').length;
          this.recentRequests = arr.slice(0, 5);
        },
        error: () => {
          this.stats[0].value = 0;
          this.recentRequests = [];
        },
      });

      this.sacService.getAll().subscribe({
        next: (sacList) => (this.stats[1].value = sacList?.length || 0),
      });

      this.personasService.getPersonas().subscribe({
        next: (pList) => (this.stats[2].value = pList?.length || 0),
      });

      this.usuariosService.getAll().subscribe({
        next: (uList) => (this.stats[3].value = uList?.length || 0),
      });

    } else {
      // Configuración de métricas para USUARIOS FIELES (Estándar)
      this.stats = [
        { title: 'Mis Solicitudes Activas', value: 0, icon: 'bi-file-earmark-text', color: 'primary' },
        { title: 'Mis Certificados', value: 0, icon: 'bi-patch-check', color: 'success' },
        { title: 'Mis Notificaciones', value: 0, icon: 'bi-bell', color: 'warning' },
        { title: 'Eventos Parroquiales', value: 0, icon: 'bi-calendar3', color: 'danger' },
      ];

      this.solService.getMisSolicitudes().subscribe({
        next: (list) => {
          const arr = list || [];
          this.stats[0].value = arr.filter((s: any) => s.estado === 'Pendiente' || s.estado === 'pendiente' || s.estado === 'en_revision').length;
          this.recentRequests = arr.slice(0, 5);
        },
      });

      this.certService.getCertificados().subscribe({
        next: (certList) => (this.stats[1].value = certList?.length || 0),
      });

      this.notifService.getNotificaciones().subscribe({
        next: (nList) => (this.stats[2].value = nList?.filter((n) => !n.leida).length || 0),
      });

      this.eventosService.getEventos().subscribe({
        next: (eList) => (this.stats[3].value = eList?.length || 0),
      });
    }

    this.cargando = false;
  }
}