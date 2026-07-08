import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-sacramentos-list',
  imports: [CommonModule],
  templateUrl: './sacramentos-list.html',
  styleUrl: './sacramentos-list.scss',
})
export class SacramentosListComponent {
  sacramentos = [
    { nombre: 'Bautismo', requisitos: 4, estado: 'Activo' },
    { nombre: 'Confirmación', requisitos: 3, estado: 'Activo' },
    { nombre: 'Primera Comunión', requisitos: 5, estado: 'Activo' },
    { nombre: 'Matrimonio', requisitos: 8, estado: 'Activo' },
  ];
}
