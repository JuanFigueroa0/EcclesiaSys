import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ConfiguracionService } from '../../services/configuracion.service';
import { ConfiguracionParroquial } from '../../models/configuracion.model';

@Component({
  selector: 'app-configuracion',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './configuracion.html',
  styleUrl: './configuracion.scss',
})
export class ConfiguracionComponent implements OnInit {
  private configService = inject(ConfiguracionService);
  private fb = inject(FormBuilder);

  tabActivo = 'general';
  config: ConfiguracionParroquial | null = null;
  mensajeExito = '';

  generalForm: FormGroup = this.fb.group({
    nombre_parroquia: ['', Validators.required],
    direccion: ['', Validators.required],
    telefono: ['', Validators.required],
    email_parroquia: ['', [Validators.required, Validators.email]],
    parroco_actual: ['', Validators.required],
  });

  certificadosForm: FormGroup = this.fb.group({
    plantilla_activa: ['clasica', Validators.required],
    incluir_qr: [true],
    incluir_sello: [true],
  });

  retencionForm: FormGroup = this.fb.group({
    dias_retencion_docs: [1825, [Validators.required, Validators.min(365)]],
  });

  notificacionesForm: FormGroup = this.fb.group({
    notif_email: [true],
    notif_telegram: [false],
    telegram_bot_token: [''],
  });

  ngOnInit(): void {
    this.configService.getConfiguracion().subscribe({
      next: (data) => {
        this.config = data;
        this.generalForm.patchValue({
          nombre_parroquia: data.nombre_parroquia,
          direccion: data.direccion,
          telefono: data.telefono,
          email_parroquia: data.email_parroquia,
          parroco_actual: data.parroco_actual,
        });
        this.certificadosForm.patchValue({
          plantilla_activa: data.plantilla_activa,
          incluir_qr: data.incluir_qr,
          incluir_sello: data.incluir_sello,
        });
        this.retencionForm.patchValue({
          dias_retencion_docs: data.dias_retencion_docs,
        });
        this.notificacionesForm.patchValue({
          notif_email: data.notif_email,
          notif_telegram: data.notif_telegram,
          telegram_bot_token: data.telegram_bot_token || '',
        });
      },
    });
  }

  guardarFormulario(form: FormGroup): void {
    if (form.invalid) {
      form.markAllAsTouched();
      return;
    }

    this.configService.updateConfiguracion(form.value).subscribe({
      next: () => {
        this.mensajeExito = 'Configuración guardada exitosamente.';
        setTimeout(() => (this.mensajeExito = ''), 3000);
      },
    });
  }
}
