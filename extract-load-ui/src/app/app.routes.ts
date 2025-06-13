import { Routes } from '@angular/router';
import { AuthGuard } from './guards/auth.guard';
import { AdminGuard } from './guards/admin.guard';

export const routes: Routes = [
  { path: 'login', loadComponent: () => import('./pages/login/login').then(m => m.Login) },
  { path: 'register', loadComponent: () => import('./pages/register/register').then(m => m.Register) },
  { 
    path: 'landing',
    loadComponent: () => import('./pages/landing/landing').then(m => m.Landing),
    canActivate: [AuthGuard]
  },
  { 
    path: 'data-extraction',
    loadComponent: () => import('./pages/data-extraction/data-extraction').then(m => m.DataExtraction),
    canActivate: [AuthGuard]
  },
  { 
    path: 'scheduler',
    loadComponent: () => import('./pages/scheduler/scheduler').then(m => m.Scheduler),
    canActivate: [AuthGuard]
  },
  { 
    path: 'user-management',
    loadComponent: () => import('./pages/user-management/user-management').then(m => m.UserManagement),
    canActivate: [AuthGuard, AdminGuard]
  },
  { 
    path: 'config-list',
    loadComponent: () => import('./pages/config-list/config-list').then(m => m.ConfigListComponent),
    canActivate: [AuthGuard]
  },
  { 
    path: 'profile',
    loadComponent: () => import('./pages/profile/profile').then(m => m.ProfileComponent),
    canActivate: [AuthGuard]
  },
  { 
    path: 'logs',
    loadComponent: () => import('./pages/logs/logs').then(m => m.LogsPage),
    canActivate: [AuthGuard] // Optional: add this if logs should be protected
  },
  { path: '**', redirectTo: 'login' }
];