import { Component, OnInit, inject, signal, computed, ChangeDetectionStrategy, DestroyRef } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators, FormsModule } from '@angular/forms';
import { PersonasService } from '../../services/personas.service';
import { Persona } from '../../models/persona.model';

export interface PersonaConIniciales extends Persona {
  iniciales?: string;
}

@Component({
  selector: 'app-personas-list',
  standalone: true,
  imports: [CommonModule, RouterLink, ReactiveFormsModule, FormsModule],
  templateUrl: './personas-list.html',
  styleUrl: './personas-list.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PersonasListComponent implements OnInit {
  private personasService = inject(PersonasService);
  private fb = inject(FormBuilder);
  private destroyRef = inject(DestroyRef);

  personas = signal<PersonaConIniciales[]>([]);
  busqueda = signal<string>('');
  modalCrear = signal<boolean>(false);
  personaEditarId = signal<number | null>(null);

  personasFiltradas = computed(() => {
    const term = this.busqueda().trim().toLowerCase();
    const list = this.personas();
    if (!term) return list;
    return list.filter(
      (p) =>
        `${p.primer_nombre} ${p.primer_apellido}`.toLowerCase().includes(term) ||
        (p.numero_documento && p.numero_documento.includes(term))
    );
  });

  personaForm: FormGroup = this.fb.group({
    primer_nombre: ['', Validators.required],
    segundo_nombre: [''],
    primer_apellido: ['', Validators.required],
    segundo_apellido: [''],
    tipo_documento: ['CC', Validators.required],
    numero_documento: ['', Validators.required],
    estado_civil: ['soltero', Validators.required],
    fecha_nacimiento: [''],
    lugar_nacimiento: [''],
    sexo: ['masculino', Validators.required],
  });

  ngOnInit(): void {
    this.cargarPersonas();
  }

  cargarPersonas(): void {
    this.personasService.getPersonas().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (data) => {
        const result = (data || []).map((p) => ({
          ...p,
          iniciales: `${p.primer_nombre?.charAt(0) || ''}${p.primer_apellido?.charAt(0) || ''}`.toUpperCase(),
        }));
        this.personas.set(result);
      },
      error: (err) => {
        console.error('Error cargando personas:', err);
        this.personas.set([]);
      },
    });
  }

  onBusquedaChange(val: string): void {
    this.busqueda.set(val);
  }

  abrirModalCrear(): void {
    this.personaEditarId.set(null);
    this.personaForm.reset({
      tipo_documento: 'CC',
      estado_civil: 'soltero',
      sexo: 'masculino',
    });
    this.modalCrear.set(true);
  }

  abrirModalEditar(persona: Persona): void {
    this.personaEditarId.set(persona.id);
    this.personaForm.patchValue({
      primer_nombre: persona.primer_nombre,
      segundo_nombre: persona.segundo_nombre || '',
      primer_apellido: persona.primer_apellido,
      segundo_apellido: persona.segundo_apellido || '',
      tipo_documento: persona.tipo_documento,
      numero_documento: persona.numero_documento,
      estado_civil: persona.estado_civil || 'soltero',
      fecha_nacimiento: persona.fecha_nacimiento || '',
      lugar_nacimiento: persona.lugar_nacimiento || '',
      sexo: persona.sexo || 'masculino',
    });
    this.modalCrear.set(true);
  }

  cerrarModal(): void {
    this.modalCrear.set(false);
  }

  guardarPersona(): void {
    if (this.personaForm.invalid) {
      this.personaForm.markAllAsTouched();
      return;
    }

    const payload = this.personaForm.value;
    const editarId = this.personaEditarId();
    if (editarId) {
      this.personasService.updatePersona(editarId, payload).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
        next: () => {
          this.cargarPersonas();
          this.cerrarModal();
        },
      });
    } else {
      this.personasService.createPersona(payload).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
        next: () => {
          this.cargarPersonas();
          this.cerrarModal();
        },
      });
    }
  }
}
