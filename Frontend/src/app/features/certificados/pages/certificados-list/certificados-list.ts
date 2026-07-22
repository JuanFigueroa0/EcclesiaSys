import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators, FormsModule } from '@angular/forms';
import { CertificadosService } from '../../services/certificados.service';
import { Certificado } from '../../models/certificado.model';
import { TokenService } from '../../../../core/services/token';
import { PerfilService } from '../../../perfil/services/perfil.service';

@Component({
  selector: 'app-certificados-list',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  templateUrl: './certificados-list.html',
  styleUrl: './certificados-list.scss',
})
export class CertificadosListComponent implements OnInit {
  private certService = inject(CertificadosService);
  private tokenService = inject(TokenService);
  private perfilService = inject(PerfilService);
  private fb = inject(FormBuilder);

  certificados: Certificado[] = [];
  busqueda = '';
  modalGenerar = false;
  userEmail = '';
  userName = '';

  session = signal<any>(this.tokenService.getUserData());

  get esAdmin(): boolean {
    const roles: string[] = this.session()?.roles ?? [];
    const rolesAdmin = ['superadmin', 'administrador parroquial', 'secretario', 'párroco', 'parroco'];
    return roles.some((r) => rolesAdmin.includes(r.toLowerCase().trim()));
  }

  certForm: FormGroup = this.fb.group({
    tipo: ['bautismo', Validators.required],
    persona_nombre: ['', Validators.required],
    solicitante: ['', Validators.required],
  });

  ngOnInit(): void {
    const sessionAny = this.session() as any;
    this.userEmail = sessionAny?.correo || sessionAny?.email || '';

    this.perfilService.getPerfil().subscribe({
      next: (p) => {
        if (p) {
          this.userName = `${p.primer_nombre ?? ''} ${p.primer_apellido ?? ''}`.trim();
        }
        this.cargar();
      },
      error: () => this.cargar(),
    });
  }

  cargar(): void {
    this.certService.getCertificados().subscribe({
      next: (data) => {
        const list = data || [];
        if (this.esAdmin) {
          this.certificados = list;
        } else {
          // Usuario Fiel: filtrar solo los certificados a su nombre o solicitados por su cuenta
          const searchTerm = (this.userName || this.userEmail).toLowerCase().trim();
          if (!searchTerm) {
            this.certificados = [];
          } else {
            this.certificados = list.filter((c) => {
              const sol = (c.solicitante || '').toLowerCase();
              const tit = (c.persona_nombre || '').toLowerCase();
              return sol.includes(searchTerm) || tit.includes(searchTerm) || searchTerm.includes(sol) || searchTerm.includes(tit);
            });
          }
        }
      },
      error: () => (this.certificados = []),
    });
  }

  get filtrados(): Certificado[] {
    if (!this.busqueda.trim()) return this.certificados;
    const t = this.busqueda.toLowerCase();
    return this.certificados.filter(
      (c) => c.persona_nombre.toLowerCase().includes(t) || c.codigo.toLowerCase().includes(t)
    );
  }

  abrirModal(): void {
    this.certForm.reset({ tipo: 'bautismo' });
    this.modalGenerar = true;
  }

  cerrarModal(): void {
    this.modalGenerar = false;
  }

  generar(): void {
    if (this.certForm.invalid) {
      this.certForm.markAllAsTouched();
      return;
    }

    this.certService.generarCertificado(this.certForm.value).subscribe({
      next: () => {
        this.cargar();
        this.cerrarModal();
      },
    });
  }

  descargar(c: Certificado): void {
    alert(`Descargando certificado oficial PDF [${c.codigo}]...`);
  }
}
