import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators, FormsModule } from '@angular/forms';
import { PagosService } from '../../services/pagos.service';
import { Pago } from '../../models/pago.model';

@Component({
  selector: 'app-pagos-list',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  templateUrl: './pagos-list.html',
  styleUrl: './pagos-list.scss',
})
export class PagosListComponent implements OnInit {
  private pagosService = inject(PagosService);
  private fb = inject(FormBuilder);

  pagos: Pago[] = [];
  busqueda = '';
  modalCrear = false;

  pagoForm: FormGroup = this.fb.group({
    fiel_nombre: ['', Validators.required],
    concepto: ['', Validators.required],
    monto: [25000, [Validators.required, Validators.min(1000)]],
    metodo: ['efectivo', Validators.required],
  });

  ngOnInit(): void {
    this.cargar();
  }

  cargar(): void {
    this.pagosService.getPagos().subscribe({
      next: (data) => (this.pagos = data),
    });
  }

  get filtrados(): Pago[] {
    if (!this.busqueda.trim()) return this.pagos;
    const t = this.busqueda.toLowerCase();
    return this.pagos.filter(
      (p) => p.fiel_nombre.toLowerCase().includes(t) || p.referencia.toLowerCase().includes(t) || p.concepto.toLowerCase().includes(t)
    );
  }

  abrirModal(): void {
    this.pagoForm.reset({ monto: 25000, metodo: 'efectivo' });
    this.modalCrear = true;
  }

  cerrarModal(): void {
    this.modalCrear = false;
  }

  guardar(): void {
    if (this.pagoForm.invalid) {
      this.pagoForm.markAllAsTouched();
      return;
    }

    this.pagosService.registrarPago(this.pagoForm.value).subscribe({
      next: () => {
        this.cargar();
        this.cerrarModal();
      },
    });
  }
}
