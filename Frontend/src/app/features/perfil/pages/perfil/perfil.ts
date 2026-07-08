import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { forkJoin } from 'rxjs';
import { PerfilService } from '../../services/perfil.service';

@Component({
  selector: 'app-perfil',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './perfil.html',
  styleUrl: './perfil.scss',
})
export class PerfilComponent implements OnInit {

  private perfilService = inject(PerfilService);
  private fb = inject(FormBuilder);

  usuario: any = null;
  sesiones: any[] = [];
  sesionesCargadas = false;

  cargando = true;
  activeTab = 'info';
  perfilExiste = false;

  tiposDocumento = ['CC', 'TI', 'CE', 'Pasaporte'];

  sexos = [
    { label: 'Masculino', value: 'masculino' },
    { label: 'Femenino', value: 'femenino' }
  ];

  estadosCiviles = [
    { label: 'Soltero', value: 'soltero' },
    { label: 'Casado', value: 'casado' },
    { label: 'Unión libre', value: 'union_libre' },
    { label: 'Divorciado', value: 'divorciado' },
    { label: 'Viudo', value: 'viudo' },
    { label: 'Religioso casado', value: 'religioso_casado' },
    { label: 'Anulado', value: 'anulado' }
  ];

  perfilForm: FormGroup = this.fb.group({
    primer_nombre: ['', Validators.required],
    segundo_nombre: [''],
    primer_apellido: ['', Validators.required],
    segundo_apellido: [''],
    fecha_nacimiento: ['', Validators.required],
    sexo: ['', Validators.required],
    lugar_nacimiento: [''],
    region: [''],
    departamento: [''],
    municipio: [''],
    tipo_documento: ['', Validators.required],
    numero_documento: ['', Validators.required],
    estado_civil: [''],
  });

  emailForm: FormGroup = this.fb.group({
    nuevo_correo: ['', [Validators.required, Validators.email]],
    contrasena_actual: ['', Validators.required],
  });

  passwordForm: FormGroup = this.fb.group({
    contrasena_actual: ['', Validators.required],
    contrasena_nueva: ['', Validators.required],
    confirmar_contrasena: ['', Validators.required],
  });

  ngOnInit(): void {
    this.cargarDatosIniciales();
  }

  cargarDatosIniciales(force = false): void {
    const cachedUsuario = this.perfilService.getMeSnapshot();
    const cachedPerfil = this.perfilService.getPerfilSnapshot();
    const perfilResuelto =
      cachedPerfil !== null || this.perfilService.isPerfilNotFound();

    if (!force && cachedUsuario) {
      this.aplicarDatos(
        cachedUsuario,
        perfilResuelto ? cachedPerfil : undefined
      );
      this.cargando = false;

      if (perfilResuelto) {
        return;
      }
    } else {
      this.cargando = true;
    }

    forkJoin({
      usuario: this.perfilService.getMe(force),
      perfil: this.perfilService.getPerfil(force),
    }).subscribe({
      next: ({ usuario, perfil }) => {
        this.aplicarDatos(usuario, perfil);
        this.cargando = false;
      },
      error: (err) => {
        console.error(err);
        this.cargando = false;
      },
    });
  }

  private aplicarDatos(usuario: any, perfil: any | null | undefined): void {
    this.usuario = usuario;

    if (perfil === undefined) {
      return;
    }

    if (perfil) {
      this.perfilExiste = true;
      this.perfilForm.patchValue(perfil);
      this.perfilForm.markAsPristine();
      return;
    }

    this.perfilExiste = false;
    this.perfilForm.markAsPristine();
  }

  cambiarTab(tab: string): void {
    this.activeTab = tab;

    if (tab === 'sessions' && !this.sesionesCargadas) {
      this.cargarSesiones();
    }
  }

  cargarSesiones(): void {
    this.perfilService.getSesiones().subscribe({
      next: (data: any) => {
        this.sesiones = data;
        this.sesionesCargadas = true;
      },
      error: console.error,
    });
  }

  guardarPerfil(): void {
    if (this.perfilForm.invalid) {
      this.perfilForm.markAllAsTouched();
      return;
    }

    const valores = this.perfilForm.value;

    const request = this.perfilExiste
      ? this.perfilService.actualizarPerfil(valores)
      : this.perfilService.crearPerfil(valores);

    request.subscribe({
      next: (res) => {
        alert('Perfil guardado correctamente');
        this.perfilExiste = true;
        this.perfilForm.patchValue(res);
        this.perfilForm.markAsPristine();
      },
      error: console.error,
    });
  }

  actualizarCorreo(): void {
    if (this.emailForm.invalid) {
      this.emailForm.markAllAsTouched();
      return;
    }

    this.perfilService.cambiarEmail(this.emailForm.value).subscribe({
      next: () => alert('Correo actualizado'),
      error: console.error,
    });
  }

  actualizarPassword(): void {
    if (this.passwordForm.invalid) {
      this.passwordForm.markAllAsTouched();
      return;
    }

    this.perfilService.cambiarPassword(this.passwordForm.value).subscribe({
      next: () => alert('Contraseña actualizada'),
      error: console.error,
    });
  }

  hayCambios(): boolean {
    if (!this.perfilExiste) {
      return true;
    }
    return this.perfilForm.dirty;
  }

  passwordCoincide(): boolean {
    const p = this.passwordForm.value;
    return p.contrasena_nueva === p.confirmar_contrasena;
  }

  get inicialAvatar(): string {
    const nombre = this.perfilForm.get('primer_nombre')?.value;
    return nombre?.charAt(0)?.toUpperCase() || 'U';
  }
}