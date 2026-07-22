import { Component, OnInit, inject } from '@angular/core';
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
})
export class PersonaDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private personasService = inject(PersonasService);

  persona: Persona | null = null;
  cargando = true;

  sacramentosRegistrados = [
    { nombre: 'Bautismo', fecha: '2010-06-12', parroquia: 'Parroquia San José', libro: 'B-12', folio: '45' },
    { nombre: 'Confirmación', fecha: '2018-11-20', parroquia: 'Parroquia San José', libro: 'C-08', folio: '112' },
  ];

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (id) {
      this.personasService.getPersonaById(id).subscribe({
        next: (data) => {
          this.persona = data || null;
          this.cargando = false;
        },
        error: () => (this.cargando = false),
      });
    }
  }

  get iniciales(): string {
    if (!this.persona) return 'P';
    return `${this.persona.primer_nombre.charAt(0)}${this.persona.primer_apellido.charAt(0)}`.toUpperCase();
  }
}
