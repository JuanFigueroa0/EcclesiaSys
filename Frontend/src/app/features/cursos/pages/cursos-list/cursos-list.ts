import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { CursosService } from '../../services/cursos.service';
import { Curso } from '../../models/curso.model';
import { TokenService } from '../../../../core/services/token';

@Component({
  selector: 'app-cursos-list',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './cursos-list.html',
  styleUrl: './cursos-list.scss',
})
export class CursosListComponent implements OnInit {
  private cursosService = inject(CursosService);
  private tokenService = inject(TokenService);
  private fb = inject(FormBuilder);

  cursos: Curso[] = [];
  modalCrear = false;

  session = signal<any>(this.tokenService.getUserData());

  get esAdmin(): boolean {
    const roles: string[] = this.session()?.roles ?? [];
    const rolesAdmin = ['superadmin', 'administrador parroquial', 'secretario', 'párroco', 'parroco'];
    return roles.some((r) => rolesAdmin.includes(r.toLowerCase().trim()));
  }

  cursoForm: FormGroup = this.fb.group({
    nombre: ['', Validators.required],
    sacramento: ['Confirmación', Validators.required],
    catequista: ['', Validators.required],
    fecha_inicio: ['', Validators.required],
    fecha_fin: ['', Validators.required],
  });

  ngOnInit(): void {
    this.cargar();
  }

  cargar(): void {
    this.cursosService.getCursos().subscribe({
      next: (data) => (this.cursos = data || []),
      error: () => (this.cursos = []),
    });
  }

  abrirModal(): void {
    this.cursoForm.reset({ sacramento: 'Confirmación' });
    this.modalCrear = true;
  }

  cerrarModal(): void {
    this.modalCrear = false;
  }

  guardar(): void {
    if (this.cursoForm.invalid) {
      this.cursoForm.markAllAsTouched();
      return;
    }

    this.cursosService.crearCurso(this.cursoForm.value).subscribe({
      next: () => {
        this.cargar();
        this.cerrarModal();
      },
    });
  }
}
