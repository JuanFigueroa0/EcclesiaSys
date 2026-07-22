import { Routes } from '@angular/router';
import { AuthLayoutComponent } from './layouts/auth-layout/auth-layout';
import { MainLayoutComponent } from './layouts/main-layout/main-layout';

import { LoginComponent } from './features/auth/pages/login/login';
import { RegisterComponent } from './features/auth/pages/register/register';
import { ForgotPasswordComponent } from './features/auth/pages/forgot-password/forgot-password';
import { ResetPasswordComponent } from './features/auth/pages/reset-password/reset-password';
import { VerifyEmailComponent } from './features/auth/pages/verify-email/verify-email';

import { DashboardComponent } from './features/dashboard/pages/dashboard/dashboard';
import { PerfilComponent } from './features/perfil/pages/perfil/perfil';
import { UsuariosListComponent } from './features/usuarios/pages/usuarios-list/usuarios-list';
import { RolesListComponent } from './features/roles/pages/roles-list/roles-list';
import { SacramentosListComponent } from './features/sacramentos/pages/sacramentos-list/sacramentos-list';
import { SolicitudesListComponent } from './features/solicitudes/pages/solicitudes-list/solicitudes-list';
import { PersonasListComponent } from './features/personas/pages/personas-list/personas-list';
import { PersonaDetailComponent } from './features/personas/pages/persona-detail/persona-detail';
import { EventosListComponent } from './features/eventos/pages/eventos-list/eventos-list';
import { NotificacionesListComponent } from './features/notificaciones/pages/notificaciones-list/notificaciones-list';
import { ConfiguracionComponent } from './features/configuracion/pages/configuracion/configuracion';
import { CertificadosListComponent } from './features/certificados/pages/certificados-list/certificados-list';
import { CursosListComponent } from './features/cursos/pages/cursos-list/cursos-list';
import { PagosListComponent } from './features/pagos/pages/pagos-list/pagos-list';
import { AuditoriaListComponent } from './features/auditoria/pages/auditoria-list/auditoria-list';
import { authGuard } from './core/guards/auth-guard';
import { roleGuard } from './core/guards/role-guard';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'auth/login',
    pathMatch: 'full',
  },
  {
    path: 'auth',
    component: AuthLayoutComponent,
    children: [
      { path: 'login', component: LoginComponent },
      { path: 'register', component: RegisterComponent },
      { path: 'forgot-password', component: ForgotPasswordComponent },
      { path: 'reset-password', component: ResetPasswordComponent },
      { path: 'verify-email', component: VerifyEmailComponent },
      { path: '', redirectTo: 'login', pathMatch: 'full' },
    ],
  },
  {
    path: 'app',
    component: MainLayoutComponent,
    canActivate: [authGuard],
    children: [
      { path: 'dashboard', component: DashboardComponent },
      { path: 'perfil', component: PerfilComponent },
      { path: 'solicitudes', component: SolicitudesListComponent },
      { path: 'notificaciones', component: NotificacionesListComponent },
      { path: 'eventos', component: EventosListComponent },
      { path: 'certificados', component: CertificadosListComponent },
      { path: 'cursos', component: CursosListComponent },

      // Rutas administrativas con restricción estricta
      {
        path: 'sacramentos',
        component: SacramentosListComponent,
        canActivate: [roleGuard],
        data: { roles: ['Superadmin', 'Administrador Parroquial', 'Secretario', 'Párroco'] },
      },
      {
        path: 'personas',
        component: PersonasListComponent,
        canActivate: [roleGuard],
        data: { roles: ['Superadmin', 'Administrador Parroquial', 'Secretario', 'Párroco'] },
      },
      {
        path: 'personas/:id',
        component: PersonaDetailComponent,
        canActivate: [roleGuard],
        data: { roles: ['Superadmin', 'Administrador Parroquial', 'Secretario', 'Párroco'] },
      },
      {
        path: 'pagos',
        component: PagosListComponent,
        canActivate: [roleGuard],
        data: { roles: ['Superadmin', 'Administrador Parroquial', 'Secretario'] },
      },
      {
        path: 'usuarios',
        component: UsuariosListComponent,
        canActivate: [roleGuard],
        data: { roles: ['Superadmin', 'Administrador Parroquial'] },
      },
      {
        path: 'configuracion',
        component: ConfiguracionComponent,
        canActivate: [roleGuard],
        data: { roles: ['Superadmin', 'Administrador Parroquial'] },
      },
      {
        path: 'roles',
        component: RolesListComponent,
        canActivate: [roleGuard],
        data: { roles: ['Superadmin'] },
      },
      {
        path: 'auditoria',
        component: AuditoriaListComponent,
        canActivate: [roleGuard],
        data: { roles: ['Superadmin'] },
      },
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
    ],
  },
  {
    path: '**',
    redirectTo: 'auth/login',
  },
];