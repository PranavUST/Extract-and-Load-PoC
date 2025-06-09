import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { PipelineService } from './pipeline.service';

@Component({
  selector: 'app-data-template',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatInputModule,
    MatFormFieldModule
  ],
  templateUrl: './data-template.html',
  styleUrl: './data-template.scss'
})
export class DataTemplateComponent {
  configFile = '';
  status = '';

  constructor(private pipelineService: PipelineService) {}

  runPipeline(): void {
    if (!this.configFile.trim()) {
      this.status = 'Error: Please enter a config file path';
      return;
    }

    this.pipelineService.runPipeline(this.configFile).subscribe({
      next: (res) => {
        this.status = 'Pipeline started!';
        console.log('Pipeline response:', res);
      },
      error: (err) => {
        console.error('Pipeline error:', err);
        this.status = 'Error: ' + (err.error?.message || err.message || 'Unknown error occurred');
      }
    });
  }

  checkStatus(): void {
    this.pipelineService.getStatus().subscribe({
      next: (res) => {
        this.status = `Status: ${res.status}${res.message ? ' - ' + res.message : ''}`;
      },
      error: (err) => {
        console.error('Status check error:', err);
        this.status = 'Error: ' + (err.error?.message || err.message || 'Failed to check status');
      }
    });
  }
}