import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

interface ExtractionTemplate {
  id: number;
  name: string;
  sourceType: string;
  targetType: string;
}

@Component({
  standalone: true,
  selector: 'app-template-list',
  templateUrl: './template-list.html',
  imports: [
    CommonModule,
    MatTableModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule
  ]
})
export class TemplateList {
  templates: ExtractionTemplate[] = [
    { id: 1, name: 'Customer Sync', sourceType: 'API', targetType: 'CSV' },
    { id: 2, name: 'Inventory FTP', sourceType: 'FTP', targetType: 'Database' }
  ];

  editTemplate(t: ExtractionTemplate) {
    alert('Edit template: ' + t.name);
  }

  deleteTemplate(t: ExtractionTemplate) {
    this.templates = this.templates.filter(x => x.id !== t.id);
  }

  createNewTemplate() {
    alert('Create new template');
  }
}
