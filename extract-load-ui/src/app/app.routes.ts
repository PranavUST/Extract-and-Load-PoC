import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', loadComponent: () => import('./pages/landing/landing').then(m => m.Landing) },
  { path: 'data-extraction', loadComponent: () => import('./pages/data-extraction/data-extraction').then(m => m.DataExtraction) },
  { path: 'scheduler', loadComponent: () => import('./pages/scheduler/scheduler').then(m => m.Scheduler) },
  { path: 'user-management', loadComponent: () => import('./pages/user-management/user-management').then(m => m.UserManagement) },
  { path: '**', redirectTo: '' }
];
