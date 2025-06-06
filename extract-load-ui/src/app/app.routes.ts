import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./data-template').then(m => m.DataTemplateComponent)
  },
  {
    path: 'data-template',
    loadComponent: () => import('./data-template').then(m => m.DataTemplateComponent)
  }
];