import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators, FormsModule } from '@angular/forms';
import { UsuariosService } from '../../../../core/services/usuarios';
import { RolesService } from '../../../roles/services/roles.service';
import { Rol } from '../../../roles/models/rol.model';

export interface UsuarioItem {
  id?: number;
  nombre: string;
  correo: string;
  rol: string;
  rol_id?: number | null;
  estado: string;
}

@Component({
  selector: 'app-usuarios-list',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  templateUrl: './usuarios-list.html',
  styleUrl: './usuarios-list.scss',
})
export class UsuariosListComponent implements OnInit {
  private usuariosService = inject(UsuariosService);
  private rolesService = inject(RolesService);
  private fb = inject(FormBuilder);

  usuarios: UsuarioItem[] = [];
  roles: Rol[] = [];
  cargando = true;
  guardando = false;
  busqueda = '';
  modalCrear = false;
  usuarioEditarId: number | null = null;
  mensajeError = '';

  usuarioForm: FormGroup = this.fb.group({
    correo: ['', [Validators.required, Validators.email]],
    contrasena: [''],
    rol_id: ['', Validators.required],
    estado: ['Activo', Validators.required],
  });

  ngOnInit(): void {
    this.cargarRoles();
    this.cargarUsuarios();
  }

  cargarRoles(): void {
    this.rolesService.obtenerRoles().subscribe({
      next: (list) => (this.roles = list || []),
      error: () => (this.roles = []),
    });
  }

  cargarUsuarios(): void {
    this.cargando = true;
    this.usuariosService.getAll().subscribe({
      next: (data) => {
        this.usuarios = data || [];
        this.cargando = false;
      },
      error: (err) => {
        console.warn('Error cargando usuarios desde API:', err);
        this.usuarios = [];
        this.cargando = false;
      },
    });
  }

  get usuariosFiltrados(): UsuarioItem[] {
    if (!this.busqueda.trim()) return this.usuarios;
    const term = this.busqueda.toLowerCase();
    return this.usuarios.filter(
      (u) => u.nombre.toLowerCase().includes(term) || u.correo.toLowerCase().includes(term)
    );
  }

  abrirModalCrear(): void {
    this.usuarioEditarId = null;
    this.mensajeError = '';
    this.usuarioForm.reset({
      rol_id: this.roles[0]?.id || '',
      estado: 'Activo',
      contrasena: 'Ecclesia2026*',
    });
    this.modalCrear = true;
  }

  abrirModalEditar(u: UsuarioItem): void {
    this.usuarioEditarId = u.id || null;
    this.mensajeError = '';
    this.usuarioForm.patchValue({
      correo: u.correo,
      contrasena: '',
      rol_id: u.rol_id || '',
      estado: u.estado,
    });
    this.modalCrear = true;
  }

  cerrarModal(): void {
    this.modalCrear = false;
    this.mensajeError = '';
  }

  guardarUsuario(): void {
    if (this.usuarioForm.invalid) {
      this.usuarioForm.markAllAsTouched();
      return;
    }

    this.guardando = true;
    this.mensajeError = '';
    const val = this.usuarioForm.value;

    if (this.usuarioEditarId) {
      // 1. Actualizar rol
      if (val.rol_id) {
        this.rolesService.asignarRolAUsuario(this.usuarioEditarId, Number(val.rol_id)).subscribe();
      }

      // 2. Actualizar estado (activo/inactivo)
      this.usuariosService.cambiarEstado(this.usuarioEditarId, val.estado).subscribe({
        next: () => {
          this.guardando = false;
          this.cargarUsuarios();
          this.cerrarModal();
        },
        error: (err) => {
          this.guardando = false;
          this.mensajeError = err?.error?.detail || 'No se pudo actualizar el estado del usuario.';
        },
      });
    } else {
      // Crear nueva cuenta de usuario vía /auth/register
      const payload = {
        correo: val.correo,
        contrasena: val.contrasena || 'Ecclesia2026*',
      };

      this.usuariosService.create(payload).subscribe({
        next: (res) => {
          const newUserId = res?.id;
          if (newUserId && val.rol_id) {
            this.rolesService.asignarRolAUsuario(newUserId, Number(val.rol_id)).subscribe();
          }
          if (newUserId && val.estado) {
            this.usuariosService.cambiarEstado(newUserId, val.estado).subscribe();
          }
          this.guardando = false;
          this.cargarUsuarios();
          this.cerrarModal();
        },
        error: (err) => {
          this.guardando = false;
          this.mensajeError = err?.error?.detail || 'No se pudo registrar el usuario. Verifique si el correo ya existe.';
        },
      });
    }
  }

  toggleEstado(u: UsuarioItem): void {
    if (!u.id) return;
    const nuevoEstado = u.estado === 'Activo' ? 'Inactivo' : 'Activo';
    this.usuariosService.cambiarEstado(u.id, nuevoEstado).subscribe({
      next: () => (u.estado = nuevoEstado),
      error: (err) => console.error('Error al cambiar estado:', err),
    });
  }

  eliminarUsuario(u: UsuarioItem): void {
    if (!u.id) return;
    if (confirm(`¿Está seguro de eliminar al usuario ${u.correo}?`)) {
      this.usuariosService.delete(u.id).subscribe({
        next: () => this.cargarUsuarios(),
        error: () => this.cargarUsuarios(),
      });
    }
  }
}