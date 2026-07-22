import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators, FormsModule } from '@angular/forms';
import { PersonasService } from '../../services/personas.service';
import { Persona } from '../../models/persona.model';

@Component({
  selector: 'app-personas-list',
  standalone: true,
  imports: [CommonModule, RouterLink, ReactiveFormsModule, FormsModule],
  templateUrl: './personas-list.html',
  styleUrl: './personas-list.scss',
})
export class PersonasListComponent implements OnInit {
  private personasService = inject(PersonasService);
  private fb = inject(FormBuilder);

  personas: Persona[] = [];
  busqueda = '';
  modalCrear = false;
  personaEditarId: number | null = null;

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
    this.personasService.getPersonas().subscribe({
      next: (data) => (this.personas = data),
      error: (err) => console.error('Error cargando personas:', err),
    });
  }

  get personasFiltradas(): Persona[] {
    if (!this.busqueda.trim()) return this.personas;
    const term = this.busqueda.toLowerCase();
    return this.personas.filter(
      (p) =>
        `${p.primer_nombre} ${p.primer_apellido}`.toLowerCase().includes(term) ||
        p.numero_documento.includes(term)
    );
  }

  abrirModalCrear(): void {
    this.personaEditarId = null;
    this.personaForm.reset({
      tipo_documento: 'CC',
      estado_civil: 'soltero',
      sexo: 'masculino',
    });
    this.modalCrear = true;
  }

  abrirModalEditar(persona: Persona): void {
    this.personaEditarId = persona.id;
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
    this.modalCrear = true;
  }

  cerrarModal(): void {
    this.modalCrear = false;
  }

  guardarPersona(): void {
    if (this.personaForm.invalid) {
      this.personaForm.markAllAsTouched();
      return;
    }

    const payload = this.personaForm.value;
    if (this.personaEditarId) {
      this.personasService.updatePersona(this.personaEditarId, payload).subscribe({
        next: () => {
          this.cargarPersonas();
          this.cerrarModal();
        },
      });
    } else {
      this.personasService.createPersona(payload).subscribe({
        next: () => {
          this.cargarPersonas();
          this.cerrarModal();
        },
      });
    }
  }

  getIniciales(persona: Persona): string {
    const n = persona.primer_nombre.charAt(0);
    const a = persona.primer_apellido.charAt(0);
    return `${n}${a}`.toUpperCase();
  }
}
