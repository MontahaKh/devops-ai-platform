import { Routes } from '@angular/router';
import { authGuard } from './core/auth.guard';
import { ShellComponent } from './layout/shell.component';
import { LoginComponent } from './pages/login.component';
import { RegisterComponent } from './pages/register.component';
import { DashboardComponent } from './pages/dashboard.component';
import { ProjectsComponent } from './pages/projects.component';
import { PipelinesComponent } from './pages/pipelines.component';
import { RunsComponent } from './pages/runs.component';
import { TerraformFilesComponent } from './pages/terraform-files.component';
import { RunLogsComponent } from './pages/run-logs.component';
import { ValidationLogsComponent } from './pages/validation-logs.component';
import { ProfileComponent } from './pages/profile.component';
import { AdminDashboardComponent } from './pages/admin-dashboard.component';
import { AdminUsersComponent } from './pages/admin-users.component';
import { adminGuard } from './core/admin.guard';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  {
    path: '',
    component: ShellComponent,
    canActivate: [authGuard],
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'dashboard' },
      { path: 'dashboard', component: DashboardComponent },
      { path: 'projects', component: ProjectsComponent },
      { path: 'pipelines', component: PipelinesComponent },
      { path: 'runs', component: RunsComponent },
      { path: 'validation-logs', component: ValidationLogsComponent },
      { path: 'terraform-files', component: TerraformFilesComponent },
      { path: 'runs/:id/logs', component: RunLogsComponent },
      { path: 'profile', component: ProfileComponent },
      { path: 'admin', component: AdminDashboardComponent, canActivate: [adminGuard] },
      { path: 'users', component: AdminUsersComponent, canActivate: [adminGuard] },
    ],
  },
  { path: '**', redirectTo: '' },
];
