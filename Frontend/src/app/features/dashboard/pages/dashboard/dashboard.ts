import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-dashboard',
  imports: [CommonModule, RouterLink],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
})
export class DashboardComponent {
  stats = [
    { title: 'Solicitudes activas', value: 18, icon: 'bi-file-earmark-text', color: 'primary' },
    { title: 'Sacramentos', value: 7, icon: 'bi-journal-bookmark', color: 'success' },
    { title: 'Usuarios registrados', value: 124, icon: 'bi-people', color: 'warning' },
    { title: 'Roles activos', value: 5, icon: 'bi-shield-lock', color: 'danger' },
  ];

  recentRequests = [
    { nombre: 'María González', tipo: 'Bautismo', estado: 'Pendiente', fecha: '2026-06-15' },
    { nombre: 'Carlos Pérez', tipo: 'Confirmación', estado: 'Aprobada', fecha: '2026-06-14' },
    { nombre: 'Ana Torres', tipo: 'Matrimonio', estado: 'En revisión', fecha: '2026-06-13' },
    { nombre: 'Luis Rojas', tipo: 'Comunión', estado: 'Pendiente', fecha: '2026-06-12' },
  ];
}