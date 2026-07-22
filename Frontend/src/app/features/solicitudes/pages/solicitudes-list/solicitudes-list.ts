import { Component, OnInit, inject, signal, computed, ChangeDetectionStrategy, DestroyRef } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
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
  usuario_correo?: string;
  sacramento: string;
  sacramento_id?: number;
  estado: string;
  raw_estado?: string;
  fecha: string;
  observaciones?: string;
  observaciones_secretario?: string;
  motivo?: string;
  personas?: any[];
  documentos?: any[];
}

@Component({
  selector: 'app-solicitudes-list',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  templateUrl: './solicitudes-list.html',
  styleUrl: './solicitudes-list.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SolicitudesListComponent implements OnInit {
  private solService = inject(SolicitudesService);
  private sacService = inject(SacramentosService);
  private tokenService = inject(TokenService);
  private perfilService = inject(PerfilService);
  private router = inject(Router);
  private fb = inject(FormBuilder);
  private destroyRef = inject(DestroyRef);

  solicitudes = signal<SolicitudItem[]>([]);
  sacramentos = signal<any[]>([]);
  busqueda = signal<string>('');
  modalCrear = signal<boolean>(false);
  archivoAdjunto = signal<File | null>(null);
  cargando = signal<boolean>(false);
  mensajeError = signal<string>('');

  // Modal Detalle
  modalDetalle = signal<boolean>(false);
  solicitudSeleccionada = signal<any>(null);
  cargandoDetalle = signal<boolean>(false);
  nuevoEstadoDetalle = signal<string>('pendiente');
  observacionesSecretario = signal<string>('');
  guardandoEstado = signal<boolean>(false);

  perfilInfo = signal<any>(null);
  perfilCompleto = signal<boolean>(false);

  session = signal<any>(this.tokenService.getUserData());

  esAdmin = computed(() => {
    const roles: string[] = this.session()?.roles ?? [];
    const rolesAdmin = ['superadmin', 'administrador parroquial', 'secretario', 'secretaria', 'párroco', 'parroco', 'admin'];
    return roles.some((r) => rolesAdmin.includes(r.toLowerCase().trim()));
  });

  filtradas = computed(() => {
    const query = this.busqueda().trim().toLowerCase();
    const list = this.solicitudes();
    if (!query) return list;
    return list.filter(
      (s) =>
        (s.fiel && s.fiel.toLowerCase().includes(query)) ||
        (s.usuario_correo && s.usuario_correo.toLowerCase().includes(query)) ||
        (s.sacramento && s.sacramento.toLowerCase().includes(query))
    );
  });

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
    this.perfilService.getPerfil().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (p) => {
        if (p && p.primer_nombre && p.primer_apellido) {
          this.perfilInfo.set(p);
          this.perfilCompleto.set(true);
        } else {
          this.perfilInfo.set(null);
          this.perfilCompleto.set(false);
        }
      },
      error: () => {
        this.perfilInfo.set(null);
        this.perfilCompleto.set(false);
      },
    });
  }

  cargarSacramentos(): void {
    this.sacService.getAll().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (data) => this.sacramentos.set(data || []),
      error: () => this.sacramentos.set([]),
    });
  }

  cargarSolicitudes(): void {
    const obs = this.esAdmin() ? this.solService.getAll() : this.solService.getMisSolicitudes();
    obs.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (data) => {
        this.solicitudes.set(data || []);
      },
      error: () => this.solicitudes.set([]),
    });
  }

  onBusquedaChange(val: string): void {
    this.busqueda.set(val);
  }

  abrirModal(): void {
    this.mensajeError.set('');
    const perfil = this.perfilInfo();
    this.solForm.reset({
      sacramento_id: '',
      tipo_documento: perfil?.tipo_documento || 'CC',
      primer_nombre: perfil?.primer_nombre || '',
      segundo_nombre: perfil?.segundo_nombre || '',
      primer_apellido: perfil?.primer_apellido || '',
      segundo_apellido: perfil?.segundo_apellido || '',
      numero_documento: perfil?.numero_documento || '',
      tipo_documento_adjunto: 'documento_identidad',
    });
    this.archivoAdjunto.set(null);
    this.modalCrear.set(true);
  }

  cerrarModal(): void {
    this.modalCrear.set(false);
    this.archivoAdjunto.set(null);
    this.mensajeError.set('');
  }

  verDetalle(s: SolicitudItem): void {
    this.cargandoDetalle.set(true);
    this.solicitudSeleccionada.set(s);
    this.nuevoEstadoDetalle.set(s.raw_estado || 'pendiente');
    this.observacionesSecretario.set(s.observaciones_secretario || s.observaciones || '');
    this.modalDetalle.set(true);

    if (s.id) {
      this.solService.getById(s.id).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
        next: (det) => {
          this.cargandoDetalle.set(false);
          if (det) {
            this.solicitudSeleccionada.set({
              ...s,
              ...det,
              fiel: s.fiel,
              sacramento: s.sacramento,
            });
            this.nuevoEstadoDetalle.set(det.estado || s.raw_estado || 'pendiente');
            this.observacionesSecretario.set(det.observaciones_secretario || det.observaciones || '');
          }
        },
        error: () => this.cargandoDetalle.set(false),
      });
    } else {
      this.cargandoDetalle.set(false);
    }
  }

  cerrarModalDetalle(): void {
    this.modalDetalle.set(false);
    this.solicitudSeleccionada.set(null);
  }

  guardarNuevoEstado(): void {
    const sol = this.solicitudSeleccionada();
    if (!sol || !sol.id) return;

    this.guardandoEstado.set(true);
    const estado = this.nuevoEstadoDetalle();
    const obs = this.observacionesSecretario();

    this.solService.update(sol.id, { estado, observaciones_secretario: obs }).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: () => {
        this.guardandoEstado.set(false);
        this.cerrarModalDetalle();
        this.cargarSolicitudes();
      },
      error: (err) => {
        console.error('Error al actualizar estado de la solicitud:', err);
        this.guardandoEstado.set(false);
        this.cerrarModalDetalle();
        this.cargarSolicitudes();
      },
    });
  }

  irAPerfil(): void {
    this.cerrarModal();
    this.router.navigate(['/app/perfil']);
  }

  onFileSelected(event: any): void {
    const file = event.target.files?.[0];
    if (file) {
      this.archivoAdjunto.set(file);
    }
  }

  guardar(): void {
    if (!this.perfilCompleto() && !this.esAdmin()) {
      this.mensajeError.set('Debes completar tu perfil de usuario antes de radicar una solicitud.');
      return;
    }

    if (this.solForm.invalid) {
      this.solForm.markAllAsTouched();
      return;
    }

    this.cargando.set(true);
    this.mensajeError.set('');
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

    const adjunto = this.archivoAdjunto();

    this.solService.create(payload).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (nuevaSol) => {
        if (adjunto && nuevaSol?.id) {
          this.solService
            .subirDocumento(nuevaSol.id, adjunto, val.tipo_documento_adjunto || 'requisito', 'requisito')
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
              next: () => {
                this.cargando.set(false);
                this.cargarSolicitudes();
                this.cerrarModal();
              },
              error: (err) => {
                console.error('Error al subir documento adjunto:', err);
                this.cargando.set(false);
                this.cargarSolicitudes();
                this.cerrarModal();
              },
            });
        } else {
          this.cargando.set(false);
          this.cargarSolicitudes();
          this.cerrarModal();
        }
      },
      error: (err) => {
        console.error('Error al crear solicitud:', err);
        this.cargando.set(false);
        this.mensajeError.set(err?.error?.detail || 'No se pudo radicar la solicitud. Verifique que su perfil esté completo.');
      },
    });
  }

  cambiarEstado(s: SolicitudItem, nuevoEstado: string): void {
    if (s.id) {
      this.solService.update(s.id, { estado: nuevoEstado }).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
        next: () => {
          this.cargarSolicitudes();
        },
        error: () => {
          this.cargarSolicitudes();
        },
      });
    }
  }

  getBadgeClass(estado: string): string {
    const e = (estado || '').toLowerCase();
    if (e.includes('aprob')) return 'bg-success';
    if (e.includes('recha')) return 'bg-danger';
    if (e.includes('revis')) return 'bg-info text-dark';
    if (e.includes('incomp') || e.includes('doc')) return 'bg-secondary';
    if (e.includes('cancel')) return 'bg-dark';
    return 'bg-warning text-dark';
  }
}