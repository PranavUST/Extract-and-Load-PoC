import { Routes } from '@angular/router';

export const routes: Routes = [
  { 
    path: '', 
    loadComponent: () => import('./pages/landing/landing.component').then(m => m.LandingComponent)
  },
  {
    path: 'data-extraction',
    loadChildren: () => import('./features/data-extraction/data-extraction.routes').then(m => m.DATA_EXTRACTION_ROUTES)
  },
  {
    path: 'scheduler',
    loadComponent: () => import('./features/scheduler/scheduler-config/scheduler-config.component').then(m => m.SchedulerConfigComponent)
  },
  {
    path: 'user-management',
    loadComponent: () => import('./features/user-management/user-list/user-list.component').then(m => m.UserListComponent)
  },
  { path: '**', redirectTo: '' }
];
