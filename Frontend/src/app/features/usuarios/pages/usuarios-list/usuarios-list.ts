import { Component, OnInit, inject, signal, computed, ChangeDetectionStrategy, DestroyRef } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
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
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class UsuariosListComponent implements OnInit {
  private usuariosService = inject(UsuariosService);
  private rolesService = inject(RolesService);
  private fb = inject(FormBuilder);
  private destroyRef = inject(DestroyRef);

  usuarios = signal<UsuarioItem[]>([]);
  roles = signal<Rol[]>([]);
  cargando = signal<boolean>(true);
  guardando = signal<boolean>(false);
  busqueda = signal<string>('');
  modalCrear = signal<boolean>(false);
  usuarioEditarId = signal<number | null>(null);
  mensajeError = signal<string>('');

  usuariosFiltrados = computed(() => {
    const term = this.busqueda().trim().toLowerCase();
    const list = this.usuarios();
    if (!term) return list;
    return list.filter(
      (u) =>
        (u.nombre && u.nombre.toLowerCase().includes(term)) ||
        (u.correo && u.correo.toLowerCase().includes(term))
    );
  });

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
    this.rolesService.obtenerRoles().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (list) => this.roles.set(list || []),
      error: () => this.roles.set([]),
    });
  }

  cargarUsuarios(): void {
    this.cargando.set(true);
    this.usuariosService.getAll().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (data) => {
        this.usuarios.set(data || []);
        this.cargando.set(false);
      },
      error: (err) => {
        console.warn('Error cargando usuarios desde API:', err);
        this.usuarios.set([]);
        this.cargando.set(false);
      },
    });
  }

  onBusquedaChange(val: string): void {
    this.busqueda.set(val);
  }

  abrirModalCrear(): void {
    this.usuarioEditarId.set(null);
    this.mensajeError.set('');
    const rList = this.roles();
    this.usuarioForm.reset({
      rol_id: rList[0]?.id || '',
      estado: 'Activo',
      contrasena: 'Ecclesia2026*',
    });
    this.modalCrear.set(true);
  }

  abrirModalEditar(u: UsuarioItem): void {
    this.usuarioEditarId.set(u.id || null);
    this.mensajeError.set('');
    this.usuarioForm.patchValue({
      correo: u.correo,
      contrasena: '',
      rol_id: u.rol_id || '',
      estado: u.estado,
    });
    this.modalCrear.set(true);
  }

  cerrarModal(): void {
    this.modalCrear.set(false);
    this.mensajeError.set('');
  }

  guardarUsuario(): void {
    if (this.usuarioForm.invalid) {
      this.usuarioForm.markAllAsTouched();
      return;
    }

    this.guardando.set(true);
    this.mensajeError.set('');
    const val = this.usuarioForm.value;
    const editarId = this.usuarioEditarId();

    if (editarId) {
      if (val.rol_id) {
        this.rolesService.asignarRolAUsuario(editarId, Number(val.rol_id)).pipe(takeUntilDestroyed(this.destroyRef)).subscribe();
      }

      this.usuariosService.cambiarEstado(editarId, val.estado).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
        next: () => {
          this.guardando.set(false);
          this.cargarUsuarios();
          this.cerrarModal();
        },
        error: (err) => {
          this.guardando.set(false);
          this.mensajeError.set(err?.error?.detail || 'No se pudo actualizar el estado del usuario.');
        },
      });
    } else {
      const payload = {
        correo: val.correo,
        contrasena: val.contrasena || 'Ecclesia2026*',
      };

      this.usuariosService.create(payload).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
        next: (res) => {
          const newUserId = res?.id;
          if (newUserId && val.rol_id) {
            this.rolesService.asignarRolAUsuario(newUserId, Number(val.rol_id)).pipe(takeUntilDestroyed(this.destroyRef)).subscribe();
          }
          if (newUserId && val.estado) {
            this.usuariosService.cambiarEstado(newUserId, val.estado).pipe(takeUntilDestroyed(this.destroyRef)).subscribe();
          }
          this.guardando.set(false);
          this.cargarUsuarios();
          this.cerrarModal();
        },
        error: (err) => {
          this.guardando.set(false);
          this.mensajeError.set(err?.error?.detail || 'No se pudo registrar el usuario. Verifique si el correo ya existe.');
        },
      });
    }
  }

  toggleEstado(u: UsuarioItem): void {
    if (!u.id) return;
    const nuevoEstado = u.estado === 'Activo' ? 'Inactivo' : 'Activo';
    this.usuariosService.cambiarEstado(u.id, nuevoEstado).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: () => {
        this.usuarios.update(list => list.map(item => item.id === u.id ? { ...item, estado: nuevoEstado } : item));
      },
      error: (err) => console.error('Error al cambiar estado:', err),
    });
  }

  eliminarUsuario(u: UsuarioItem): void {
    if (!u.id) return;
    if (confirm(`¿Está seguro de eliminar al usuario ${u.correo}?`)) {
      this.usuariosService.delete(u.id).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
        next: () => this.cargarUsuarios(),
        error: () => this.cargarUsuarios(),
      });
    }
  }
}