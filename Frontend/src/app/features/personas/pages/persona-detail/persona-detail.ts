import { Component, OnInit, inject, signal, computed, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { PersonasService } from '../../services/personas.service';
import { Persona } from '../../models/persona.model';

@Component({
  selector: 'app-persona-detail',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './persona-detail.html',
  styleUrl: './persona-detail.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PersonaDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private personasService = inject(PersonasService);

  persona = signal<Persona | null>(null);
  cargando = signal(true);

  sacramentosRegistrados = [
    { nombre: 'Bautismo', fecha: '2010-06-12', parroquia: 'Parroquia San José', libro: 'B-12', folio: '45' },
    { nombre: 'Confirmación', fecha: '2018-11-20', parroquia: 'Parroquia San José', libro: 'C-08', folio: '112' },
  ];

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (!id || isNaN(id)) {
      this.cargando.set(false);
      return;
    }
    this.personasService.getPersonaById(id).subscribe({
      next: (data) => {
        this.persona.set(data ?? null);
        this.cargando.set(false);
      },
      error: (err) => {
        console.error('Error al cargar persona:', err);
        this.persona.set(null);
        this.cargando.set(false);
      },
    });
  }

  iniciales = computed(() => {
    const p = this.persona();
    if (!p) return 'P';
    return `${p.primer_nombre.charAt(0)}${p.primer_apellido.charAt(0)}`.toUpperCase();
  });
}
