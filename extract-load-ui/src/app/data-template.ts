import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { PipelineService } from './pipeline.service';

@Component({
  selector: 'app-data-template',
  standalone: true,
  imports: [FormsModule, HttpClientModule],
  templateUrl: './data-template.html',
  styleUrl: './data-template.scss'
})
export class DataTemplateComponent {
  configFile = '';
  status = '';

  constructor(private pipelineService: PipelineService) {}

  runPipeline() {
    this.pipelineService.runPipeline(this.configFile).subscribe({
      next: res => this.status = 'Pipeline started!',
      error: err => {
        console.error(err); // <-- This will print the full error to the browser console
        this.status = 'Error: ' + (err.error?.message || err.message || JSON.stringify(err));
      }
    });
  }

  checkStatus() {
    this.pipelineService.getStatus().subscribe({
      next: res => this.status = `Status: ${res.status} - ${res.message}`,
      error: err => this.status = 'Error: ' + err.error.message
    });
  }
}