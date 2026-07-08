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
import { authGuard } from './core/guards/auth-guard';

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
      { path: 'usuarios', component: UsuariosListComponent },
      { path: 'roles', component: RolesListComponent },
      { path: 'sacramentos', component: SacramentosListComponent },
      { path: 'solicitudes', component: SolicitudesListComponent },
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
    ],
  },
  {
    path: '**',
    redirectTo: 'auth/login',
  },
];