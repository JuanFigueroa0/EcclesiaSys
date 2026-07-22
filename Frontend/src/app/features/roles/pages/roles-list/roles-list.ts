import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators, FormsModule } from '@angular/forms';
import { RolesService } from '../../services/roles.service';
import { PermisosService, PermisoItem } from '../../services/permisos.service';

export interface RolItem {
  id?: number;
  nombre: string;
  descripcion: string;
  es_sistema?: boolean;
}

@Component({
  selector: 'app-roles-list',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  templateUrl: './roles-list.html',
  styleUrl: './roles-list.scss',
})
export class RolesListComponent implements OnInit {
  private rolesService = inject(RolesService);
  private permisosService = inject(PermisosService);
  private fb = inject(FormBuilder);

  roles: RolItem[] = [];
  permisosDisponibles: PermisoItem[] = [];
  permisosSeleccionadosIds = new Set<number>();

  cargando = true;
  guardando = false;
  cargandoPermisosModal = false;
  modalCrear = false;
  rolEditarId: number | null = null;
  mensajeError = '';

  rolForm: FormGroup = this.fb.group({
    nombre: ['', Validators.required],
    descripcion: ['', Validators.required],
  });

  ngOnInit(): void {
    this.obtenerRoles();
    this.obtenerPermisosCat();
  }

  obtenerPermisosCat(): void {
    this.permisosService.getPermisos().subscribe({
      next: (list) => (this.permisosDisponibles = list || []),
      error: () => (this.permisosDisponibles = []),
    });
  }

  obtenerRoles(): void {
    this.cargando = true;
    this.rolesService.obtenerRoles().subscribe({
      next: (data) => {
        this.roles = data || [];
        this.cargando = false;
      },
      error: (err) => {
        console.warn('Error cargando roles desde API:', err);
        this.roles = [];
        this.cargando = false;
      },
    });
  }

  abrirModalCrear(): void {
    this.rolEditarId = null;
    this.mensajeError = '';
    this.permisosSeleccionadosIds.clear();
    this.rolForm.reset();
    this.modalCrear = true;
  }

  abrirModalEditar(r: RolItem): void {
    this.rolEditarId = r.id || null;
    this.mensajeError = '';
    this.permisosSeleccionadosIds.clear();
    this.rolForm.patchValue({
      nombre: r.nombre,
      descripcion: r.descripcion,
    });

    if (r.id) {
      this.cargandoPermisosModal = true;
      this.permisosService.getPermisosDeRol(r.id).subscribe({
        next: (pList) => {
          this.cargandoPermisosModal = false;
          if (Array.isArray(pList)) {
            pList.forEach((p) => this.permisosSeleccionadosIds.add(p.id));
          }
        },
        error: () => (this.cargandoPermisosModal = false),
      });
    }

    this.modalCrear = true;
  }

  cerrarModal(): void {
    this.modalCrear = false;
    this.mensajeError = '';
    this.permisosSeleccionadosIds.clear();
  }

  isPermisoChecked(id: number): boolean {
    return this.permisosSeleccionadosIds.has(id);
  }

  togglePermiso(id: number, event: any): void {
    if (event.target.checked) {
      this.permisosSeleccionadosIds.add(id);
    } else {
      this.permisosSeleccionadosIds.delete(id);
    }
  }

  guardarRol(): void {
    if (this.rolForm.invalid) {
      this.rolForm.markAllAsTouched();
      return;
    }

    this.guardando = true;
    this.mensajeError = '';
    const payload = this.rolForm.value;
    const permisosArray = Array.from(this.permisosSeleccionadosIds);

    if (this.rolEditarId) {
      // 1. Actualizar rol
      this.rolesService.actualizarRol(this.rolEditarId, payload).subscribe({
        next: (updatedRol) => {
          const rolId = updatedRol?.id || this.rolEditarId;
          if (rolId && permisosArray.length > 0) {
            // 2. Asignar matriz de permisos en FastAPI
            this.permisosService.asignarPermisosARol(rolId, permisosArray).subscribe({
              next: () => {
                this.guardando = false;
                this.obtenerRoles();
                this.cerrarModal();
              },
              error: () => {
                this.guardando = false;
                this.obtenerRoles();
                this.cerrarModal();
              },
            });
          } else {
            this.guardando = false;
            this.obtenerRoles();
            this.cerrarModal();
          }
        },
        error: (err) => {
          this.guardando = false;
          this.mensajeError = err?.error?.detail || 'No se pudo actualizar el rol.';
        },
      });
    } else {
      // Crear rol nuevo
      this.rolesService.crearRol(payload).subscribe({
        next: (newRol) => {
          const rolId = newRol?.id;
          if (rolId && permisosArray.length > 0) {
            this.permisosService.asignarPermisosARol(rolId, permisosArray).subscribe({
              next: () => {
                this.guardando = false;
                this.obtenerRoles();
                this.cerrarModal();
              },
              error: () => {
                this.guardando = false;
                this.obtenerRoles();
                this.cerrarModal();
              },
            });
          } else {
            this.guardando = false;
            this.obtenerRoles();
            this.cerrarModal();
          }
        },
        error: (err) => {
          this.guardando = false;
          this.mensajeError = err?.error?.detail || 'No se pudo crear el rol.';
        },
      });
    }
  }
}