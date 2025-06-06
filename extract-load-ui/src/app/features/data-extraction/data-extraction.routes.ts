import { Routes } from '@angular/router';

export const DATA_EXTRACTION_ROUTES: Routes = [
  { 
    path: 'source', 
    loadComponent: () => import('./source-config/source-config.component').then(m => m.SourceConfigComponent)
  },
  { 
    path: 'target', 
    loadComponent: () => import('./target-config/target-config.component').then(m => m.TargetConfigComponent)
  },
  { 
    path: 'templates', 
    loadComponent: () => import('./template-list/template-list.component').then(m => m.TemplateListComponent)
  },
  { path: '', redirectTo: 'source', pathMatch: 'full' }
];
