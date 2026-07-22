import { Component, OnInit, inject, signal, computed, ChangeDetectionStrategy, DestroyRef } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators, FormsModule } from '@angular/forms';
import { EventosService } from '../../services/eventos.service';
import { Evento } from '../../models/evento.model';
import { TokenService } from '../../../../core/services/token';

@Component({
  selector: 'app-eventos-list',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  templateUrl: './eventos-list.html',
  styleUrl: './eventos-list.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EventosListComponent implements OnInit {
  private eventosService = inject(EventosService);
  private tokenService = inject(TokenService);
  private fb = inject(FormBuilder);
  private destroyRef = inject(DestroyRef);

  eventos = signal<Evento[]>([]);
  filtroEstado = signal<string>('');
  filtroTipo = signal<string>('');
  modalCrear = signal<boolean>(false);

  session = signal<any>(this.tokenService.getUserData());

  esAdmin = computed(() => {
    const roles: string[] = this.session()?.roles ?? [];
    const rolesAdmin = ['superadmin', 'administrador parroquial', 'secretario', 'párroco', 'parroco'];
    return roles.some((r) => rolesAdmin.includes(r.toLowerCase().trim()));
  });

  eventosFiltrados = computed(() => {
    const estado = this.filtroEstado();
    const tipo = this.filtroTipo();
    return this.eventos().filter((e) => {
      const matchEstado = !estado || e.estado === estado;
      const matchTipo = !tipo || e.tipo === tipo;
      return matchEstado && matchTipo;
    });
  });

  eventoForm: FormGroup = this.fb.group({
    titulo: ['', Validators.required],
    tipo: ['misa', Validators.required],
    estado: ['publicado', Validators.required],
    fecha: ['', Validators.required],
    hora: ['08:00', Validators.required],
    lugar: ['', Validators.required],
    cupo: [50, [Validators.required, Validators.min(1)]],
    descripcion: [''],
  });

  ngOnInit(): void {
    this.cargarEventos();
  }

  cargarEventos(): void {
    this.eventosService.getEventos().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (data) => this.eventos.set(data || []),
      error: (err) => {
        console.error('Error cargando eventos:', err);
        this.eventos.set([]);
      },
    });
  }

  onFiltroEstadoChange(val: string): void {
    this.filtroEstado.set(val);
  }

  onFiltroTipoChange(val: string): void {
    this.filtroTipo.set(val);
  }

  abrirModal(): void {
    this.eventoForm.reset({
      tipo: 'misa',
      estado: 'publicado',
      hora: '08:00',
      cupo: 50,
    });
    this.modalCrear.set(true);
  }

  cerrarModal(): void {
    this.modalCrear.set(false);
  }

  guardarEvento(): void {
    if (this.eventoForm.invalid) {
      this.eventoForm.markAllAsTouched();
      return;
    }

    this.eventosService.createEvento(this.eventoForm.value).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: () => {
        this.cargarEventos();
        this.cerrarModal();
      },
    });
  }

  getBadgeClass(estado: string): string {
    switch (estado) {
      case 'publicado': return 'bg-success';
      case 'borrador': return 'bg-secondary';
      case 'cerrado': return 'bg-warning text-dark';
      case 'finalizado': return 'bg-info text-dark';
      case 'cancelado': return 'bg-danger';
      default: return 'bg-light text-dark';
    }
  }

  getTipoIcon(tipo: string): string {
    switch (tipo) {
      case 'misa': return 'bi-church';
      case 'retiro': return 'bi-tree';
      case 'curso': return 'bi-book';
      case 'reunion': return 'bi-people';
      default: return 'bi-calendar-event';
    }
  }
}
