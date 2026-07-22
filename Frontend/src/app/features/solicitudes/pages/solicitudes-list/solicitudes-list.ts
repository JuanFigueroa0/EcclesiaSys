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

  perfilInfo = signal<any>(null);
  perfilCompleto = signal<boolean>(false);

  session = this.tokenService.getUserData();

  esAdmin = computed(() => {
    const roles: string[] = this.session?.roles ?? [];
    const rolesAdmin = ['superadmin', 'administrador parroquial', 'secretario', 'párroco', 'parroco'];
    return roles.some((r) => rolesAdmin.includes(r.toLowerCase().trim()));
  });

  filtradas = computed(() => {
    const query = this.busqueda().trim().toLowerCase();
    const list = this.solicitudes();
    if (!query) return list;
    return list.filter(
      (s) => (s.fiel && s.fiel.toLowerCase().includes(query)) || (s.sacramento && s.sacramento.toLowerCase().includes(query))
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
          this.solicitudes.update(list => list.map(item => item.id === s.id ? { ...item, estado: nuevoEstado } : item));
        },
        error: () => {
          this.solicitudes.update(list => list.map(item => item.id === s.id ? { ...item, estado: nuevoEstado } : item));
        },
      });
    } else {
      this.solicitudes.update(list => list.map(item => item === s ? { ...item, estado: nuevoEstado } : item));
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