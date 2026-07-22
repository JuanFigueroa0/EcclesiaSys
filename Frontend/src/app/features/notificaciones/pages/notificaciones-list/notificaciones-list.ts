import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NotificacionesService } from '../../services/notificaciones.service';
import { Notificacion } from '../../models/notificacion.model';

@Component({
  selector: 'app-notificaciones-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './notificaciones-list.html',
  styleUrl: './notificaciones-list.scss',
})
export class NotificacionesListComponent implements OnInit {
  private notifService = inject(NotificacionesService);

  notificaciones: Notificacion[] = [];
  filtro = 'todas';

  ngOnInit(): void {
    this.cargar();
  }

  cargar(): void {
    this.notifService.getNotificaciones().subscribe({
      next: (data) => (this.notificaciones = data),
    });
  }

  get notificacionesFiltradas(): Notificacion[] {
    if (this.filtro === 'noleidas') {
      return this.notificaciones.filter((n) => !n.leida);
    }
    return this.notificaciones;
  }

  marcarLeida(n: Notificacion): void {
    this.notifService.marcarComoLeida(n.id).subscribe({
      next: () => this.cargar(),
    });
  }

  marcarTodasLeidas(): void {
    this.notifService.marcarTodasComoLeidas().subscribe({
      next: () => this.cargar(),
    });
  }

  getIcon(tipo: string): string {
    switch (tipo) {
      case 'solicitud': return 'bi-inbox-fill text-primary';
      case 'certificado': return 'bi-patch-check-fill text-success';
      case 'evento': return 'bi-calendar-event-fill text-info';
      case 'sistema': return 'bi-gear-fill text-secondary';
      default: return 'bi-bell-fill text-muted';
    }
  }
}
