import { Routes } from '@angular/router';
import { AuthGuard } from './guards/auth.guard';

export const routes: Routes = [
  { path: 'login', loadComponent: () => import('./pages/login/login').then(m => m.Login) },
  { path: 'register', loadComponent: () => import('./pages/register/register').then(m => m.Register) },
  { 
    path: 'landing',
    loadComponent: () => import('./pages/landing/landing').then(m => m.Landing),
    canActivate: [AuthGuard]
  },
  // Add canActivate to other protected routes
  { path: '**', redirectTo: 'login' }
];
