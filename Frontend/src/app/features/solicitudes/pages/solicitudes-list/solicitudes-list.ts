import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators, FormsModule } from '@angular/forms';
import { SolicitudesService } from '../../../../core/services/solicitudes';
import { SacramentosService } from '../../../../core/services/sacramentos';
import { TokenService } from '../../../../core/services/token';
import { PerfilService } from '../../../perfil/services/perfil.service';

export interface SolicitudItem {
  id?: number;
  fiel: string;
  sacramento: string;
  sacramento_id?: number;
  estado: string;
  fecha: string;
  observaciones?: string;
  motivo?: string;
}

@Component({
  selector: 'app-solicitudes-list',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  templateUrl: './solicitudes-list.html',
  styleUrl: './solicitudes-list.scss',
})
export class SolicitudesListComponent implements OnInit {
  private solService = inject(SolicitudesService);
  private sacService = inject(SacramentosService);
  private tokenService = inject(TokenService);
  private perfilService = inject(PerfilService);
  private router = inject(Router);
  private fb = inject(FormBuilder);

  solicitudes: SolicitudItem[] = [];
  sacramentos: any[] = [];
  busqueda = '';
  modalCrear = false;
  archivoAdjunto: File | null = null;
  cargando = false;
  mensajeError = '';

  perfilInfo: any = null;
  perfilCompleto = false;

  session = this.tokenService.getUserData();

  get esAdmin(): boolean {
    const roles: string[] = this.session?.roles ?? [];
    const rolesAdmin = ['superadmin', 'administrador parroquial', 'secretario', 'párroco', 'parroco'];
    return roles.some((r) => rolesAdmin.includes(r.toLowerCase().trim()));
  }

  solForm: FormGroup = this.fb.group({
    sacramento_id: ['', Validators.required],
    primer_nombre: ['', Validators.required],
    segundo_nombre: [''],
    primer_apellido: ['', Validators.required],
    segundo_apellido: [''],
    tipo_documento: ['CC', Validators.required],
    numero_documento: ['', Validators.required],
    fecha_preferida: [''],
    hora_preferida: [''],
    motivo: ['', Validators.required],
    observaciones: [''],
    tipo_documento_adjunto: ['documento_identidad'],
  });

  ngOnInit(): void {
    this.cargarPerfilUsuario();
    this.cargarSacramentos();
    this.cargarSolicitudes();
  }

  cargarPerfilUsuario(): void {
    this.perfilService.getPerfil().subscribe({
      next: (p) => {
        if (p && p.primer_nombre && p.primer_apellido) {
          this.perfilInfo = p;
          this.perfilCompleto = true;
        } else {
          this.perfilInfo = null;
          this.perfilCompleto = false;
        }
      },
      error: () => {
        this.perfilInfo = null;
        this.perfilCompleto = false;
      },
    });
  }

  cargarSacramentos(): void {
    this.sacService.getAll().subscribe({
      next: (data) => (this.sacramentos = data || []),
      error: () => (this.sacramentos = []),
    });
  }

  cargarSolicitudes(): void {
    const obs = this.esAdmin ? this.solService.getAll() : this.solService.getMisSolicitudes();
    obs.subscribe({
      next: (data) => {
        this.solicitudes = data || [];
      },
      error: () => (this.solicitudes = []),
    });
  }

  get filtradas(): SolicitudItem[] {
    if (!this.busqueda.trim()) return this.solicitudes;
    const t = this.busqueda.toLowerCase();
    return this.solicitudes.filter(
      (s) => s.fiel.toLowerCase().includes(t) || s.sacramento.toLowerCase().includes(t)
    );
  }

  abrirModal(): void {
    this.mensajeError = '';
    this.solForm.reset({
      sacramento_id: '',
      tipo_documento: this.perfilInfo?.tipo_documento || 'CC',
      primer_nombre: this.perfilInfo?.primer_nombre || '',
      segundo_nombre: this.perfilInfo?.segundo_nombre || '',
      primer_apellido: this.perfilInfo?.primer_apellido || '',
      segundo_apellido: this.perfilInfo?.segundo_apellido || '',
      numero_documento: this.perfilInfo?.numero_documento || '',
      tipo_documento_adjunto: 'documento_identidad',
    });
    this.archivoAdjunto = null;
    this.modalCrear = true;
  }

  cerrarModal(): void {
    this.modalCrear = false;
    this.archivoAdjunto = null;
    this.mensajeError = '';
  }

  irAPerfil(): void {
    this.cerrarModal();
    this.router.navigate(['/app/perfil']);
  }

  onFileSelected(event: any): void {
    const file = event.target.files?.[0];
    if (file) {
      this.archivoAdjunto = file;
    }
  }

  guardar(): void {
    if (!this.perfilCompleto && !this.esAdmin) {
      this.mensajeError = 'Debes completar tu perfil de usuario antes de radicar una solicitud.';
      return;
    }

    if (this.solForm.invalid) {
      this.solForm.markAllAsTouched();
      return;
    }

    this.cargando = true;
    this.mensajeError = '';
    const val = this.solForm.value;

    const payload = {
      sacramento_id: Number(val.sacramento_id),
      fecha_preferida: val.fecha_preferida ? val.fecha_preferida : null,
      hora_preferida: val.hora_preferida ? (val.hora_preferida.length === 5 ? val.hora_preferida + ':00' : val.hora_preferida) : null,
      motivo: val.motivo || 'Solicitud de sacramento',
      observaciones: val.observaciones || null,
      personas: [
        {
          rol_en_solicitud: 'receptor',
          datos_digitados: {
            primer_nombre: val.primer_nombre,
            segundo_nombre: val.segundo_nombre || null,
            primer_apellido: val.primer_apellido,
            segundo_apellido: val.segundo_apellido || null,
            tipo_documento: val.tipo_documento || 'CC',
            numero_documento: val.numero_documento || null,
          },
        },
      ],
    };

    this.solService.create(payload).subscribe({
      next: (nuevaSol) => {
        if (this.archivoAdjunto && nuevaSol?.id) {
          this.solService
            .subirDocumento(nuevaSol.id, this.archivoAdjunto, val.tipo_documento_adjunto || 'requisito', 'requisito')
            .subscribe({
              next: () => {
                this.cargando = false;
                this.cargarSolicitudes();
                this.cerrarModal();
              },
              error: (err) => {
                console.error('Error al subir documento adjunto:', err);
                this.cargando = false;
                this.cargarSolicitudes();
                this.cerrarModal();
              },
            });
        } else {
          this.cargando = false;
          this.cargarSolicitudes();
          this.cerrarModal();
        }
      },
      error: (err) => {
        console.error('Error al crear solicitud:', err);
        this.cargando = false;
        this.mensajeError = err?.error?.detail || 'No se pudo radicar la solicitud. Verifique que su perfil esté completo.';
      },
    });
  }

  cambiarEstado(s: SolicitudItem, nuevoEstado: string): void {
    if (s.id) {
      this.solService.update(s.id, { estado: nuevoEstado }).subscribe({
        next: () => (s.estado = nuevoEstado),
        error: () => (s.estado = nuevoEstado),
      });
    } else {
      s.estado = nuevoEstado;
    }
  }

  getBadgeClass(estado: string): string {
    switch (estado) {
      case 'Aprobada':
      case 'aprobada':
        return 'bg-success';
      case 'Rechazada':
      case 'rechazada':
        return 'bg-danger';
      default:
        return 'bg-warning text-dark';
    }
  }
}