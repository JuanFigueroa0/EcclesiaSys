import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators, FormsModule } from '@angular/forms';
import { SacramentosService } from '../../../../core/services/sacramentos';

export interface SacramentoItem {
  id?: number;
  nombre: string;
  requisitos: number;
  estado: string;
  libro?: string;
  folio?: string;
}

@Component({
  selector: 'app-sacramentos-list',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  templateUrl: './sacramentos-list.html',
  styleUrl: './sacramentos-list.scss',
})
export class SacramentosListComponent implements OnInit {
  private sacService = inject(SacramentosService);
  private fb = inject(FormBuilder);

  sacramentos: SacramentoItem[] = [
    { id: 1, nombre: 'Bautismo', requisitos: 4, estado: 'Activo', libro: 'B-12', folio: '45' },
    { id: 2, nombre: 'Confirmación', requisitos: 3, estado: 'Activo', libro: 'C-08', folio: '112' },
    { id: 3, nombre: 'Primera Comunión', requisitos: 5, estado: 'Activo', libro: 'PC-04', folio: '78' },
    { id: 4, nombre: 'Matrimonio', requisitos: 8, estado: 'Activo', libro: 'M-15', folio: '210' },
  ];

  busqueda = '';
  modalCrear = false;

  sacForm: FormGroup = this.fb.group({
    nombre: ['', Validators.required],
    requisitos: [3, [Validators.required, Validators.min(1)]],
    libro: ['', Validators.required],
    folio: ['', Validators.required],
    estado: ['Activo', Validators.required],
  });

  ngOnInit(): void {
    this.cargar();
  }

  cargar(): void {
    this.sacService.getAll().subscribe({
      next: (data) => {
        if (data && data.length > 0) {
          this.sacramentos = data;
        }
      },
      error: (err) => console.warn('Usando mock local de sacramentos:', err),
    });
  }

  get filtrados(): SacramentoItem[] {
    if (!this.busqueda.trim()) return this.sacramentos;
    const t = this.busqueda.toLowerCase();
    return this.sacramentos.filter((s) => s.nombre.toLowerCase().includes(t));
  }

  abrirModal(): void {
    this.sacForm.reset({ requisitos: 3, estado: 'Activo' });
    this.modalCrear = true;
  }

  cerrarModal(): void {
    this.modalCrear = false;
  }

  guardar(): void {
    if (this.sacForm.invalid) {
      this.sacForm.markAllAsTouched();
      return;
    }

    const payload = this.sacForm.value;
    this.sacramentos.push({
      id: this.sacramentos.length + 1,
      ...payload,
    });
    this.cerrarModal();
  }
}
