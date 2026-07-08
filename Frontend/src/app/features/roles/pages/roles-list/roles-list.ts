import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-roles-list',
  imports: [CommonModule],
  templateUrl: './roles-list.html',
  styleUrl: './roles-list.scss',
})
export class RolesListComponent {
  roles = [
    { nombre: 'Super Admin', permisos: 18, descripcion: 'Acceso total al sistema.' },
    { nombre: 'Administrador', permisos: 14, descripcion: 'Gestiona módulos administrativos.' },
    { nombre: 'Secretaria', permisos: 8, descripcion: 'Gestiona solicitudes y atención.' },
    { nombre: 'Usuario Fiel', permisos: 3, descripcion: 'Consulta y registra solicitudes.' },
  ];
}