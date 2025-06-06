import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatSelectModule } from '@angular/material/select';


export interface ExtractionTemplate {
  id: number;
  name: string;
  sourceType: string;
  targetType: string;
  createdDate: Date;
  isActive: boolean;
}

@Component({
  standalone: true,
  selector: 'app-template-list',
  templateUrl: './template-list.component.html',
  imports: [
    CommonModule,
    MatTableModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatSlideToggleModule,
    MatTooltipModule,
    MatSelectModule
  ]
})
export class TemplateListComponent {
  displayedColumns: string[] = ['name', 'sourceType', 'targetType', 'createdDate', 'status', 'actions'];
  templates: ExtractionTemplate[] = [
    {
      id: 1,
      name: 'Customer Data Sync',
      sourceType: 'REST API',
      targetType: 'Database',
      createdDate: new Date('2024-01-15'),
      isActive: true
    },
    {
      id: 2,
      name: 'Product Inventory',
      sourceType: 'FTP',
      targetType: 'CSV',
      createdDate: new Date('2024-02-01'),
      isActive: false
    },
    {
      id: 3,
      name: 'Sales Report',
      sourceType: 'Database',
      targetType: 'API',
      createdDate: new Date('2024-02-10'),
      isActive: true
    }
  ];

  createNewTemplate(): void {
    console.log('Creating new template...');
  }

  editTemplate(template: ExtractionTemplate): void {
    console.log('Editing template:', template);
  }

  deleteTemplate(template: ExtractionTemplate): void {
    this.templates = this.templates.filter(t => t.id !== template.id);
  }

  toggleTemplateStatus(template: ExtractionTemplate): void {
    template.isActive = !template.isActive;
  }
}
