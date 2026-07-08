import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-usuarios-list',
  imports: [CommonModule],
  templateUrl: './usuarios-list.html',
  styleUrl: './usuarios-list.scss',
})
export class UsuariosListComponent {
  usuarios = [
    { nombre: 'Samir Shaq', correo: 'admin@ecclesiasys.com', rol: 'Administrador', estado: 'Activo' },
    { nombre: 'Laura Gómez', correo: 'secretaria@ecclesiasys.com', rol: 'Secretaria', estado: 'Activo' },
    { nombre: 'Pedro Ruiz', correo: 'fiel@ecclesiasys.com', rol: 'Usuario Fiel', estado: 'Activo' },
  ];
}