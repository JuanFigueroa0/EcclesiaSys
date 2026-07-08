import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-solicitudes-list',
  imports: [CommonModule],
  templateUrl: './solicitudes-list.html',
  styleUrl: './solicitudes-list.scss',
})
export class SolicitudesListComponent {
  solicitudes = [
    { fiel: 'María González', sacramento: 'Bautismo', estado: 'Pendiente', fecha: '2026-06-15' },
    { fiel: 'Carlos Pérez', sacramento: 'Confirmación', estado: 'Aprobada', fecha: '2026-06-14' },
    { fiel: 'Lucía Romero', sacramento: 'Matrimonio', estado: 'Rechazada', fecha: '2026-06-11' },
  ];
}