import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { AuditoriaService } from '../../services/auditoria.service';
import { AuditoriaLog } from '../../models/auditoria.model';

@Component({
  selector: 'app-auditoria-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './auditoria-list.html',
  styleUrl: './auditoria-list.scss',
})
export class AuditoriaListComponent implements OnInit {
  private auditService = inject(AuditoriaService);
  private sanitizer = inject(DomSanitizer);

  logs: AuditoriaLog[] = [];
  busqueda = '';
  powerBiUrl: SafeResourceUrl;

  constructor() {
    this.powerBiUrl = this.sanitizer.bypassSecurityTrustResourceUrl(
      'https://app.powerbi.com/view?r=eyJrIjoiZTYxNTlkY2QtNjZmYy00NmQ2LTg3N2UtNTRjNTVkMzVjODk2IiwidCI6IjFlOWFhYmU4LTY3ZjgtNGYxYy1hMzI5LWE3NTRlOTI0OTlhZSIsImMiOjR9'
    );
  }

  ngOnInit(): void {
    this.cargar();
  }

  cargar(): void {
    this.auditService.getLogs().subscribe({
      next: (data) => (this.logs = data || []),
      error: () => (this.logs = []),
    });
  }

  get filtrados(): AuditoriaLog[] {
    if (!this.busqueda.trim()) return this.logs;
    const t = this.busqueda.toLowerCase();
    return this.logs.filter(
      (l) =>
        l.usuario.toLowerCase().includes(t) ||
        l.modulo.toLowerCase().includes(t) ||
        l.accion.toLowerCase().includes(t) ||
        l.detalle.toLowerCase().includes(t)
    );
  }

  getBadgeClass(accion: string): string {
    switch (accion) {
      case 'CREAR': return 'bg-success';
      case 'EDITAR': return 'bg-warning text-dark';
      case 'ELIMINAR': return 'bg-danger';
      case 'EMISION_CERTIFICADO': return 'bg-primary';
      case 'LOGIN': return 'bg-info text-dark';
      default: return 'bg-secondary';
    }
  }
}
