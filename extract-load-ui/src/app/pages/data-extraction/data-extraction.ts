import { Component, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { MatTabsModule } from '@angular/material/tabs';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { SourceConfig } from './source-config/source-config';
import { TargetConfig } from './target-config/target-config';
import { ConfigListComponent } from '../config-list/config-list';
import { HttpClient } from '@angular/common/http';
import { RouterModule } from '@angular/router';
@Component({
  standalone: true,
  selector: 'app-data-extraction',
  templateUrl: './data-extraction.html',
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatTabsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    RouterModule,
    SourceConfig,
    TargetConfig,
    ConfigListComponent
  ]
})
export class DataExtraction {
  @ViewChild(SourceConfig) sourceConfigComponent!: SourceConfig;
  schedulerForm: FormGroup;
  status = '';

  constructor(private fb: FormBuilder, private api: ApiService, private http: HttpClient) {
    this.schedulerForm = this.fb.group({
      interval: [null, [Validators.required, Validators.min(1)]],
      duration: [null, [Validators.required, Validators.min(0.1)]]
    });
  }
  runPipeline() {
    // Always get the current config from backend
    this.http.get<{source: string, target: string}>('http://localhost:5000/current-config').subscribe({
      next: (current) => {
        // Now get the actual source config object
        this.http.get<any[]>('http://localhost:5000/saved-source-configs').subscribe({
          next: (sources) => {
            const sourceObj = sources.find(s => s.name === current.source);
            let config_file = 'config/api_config.yaml'; // default
            if (sourceObj && sourceObj.type && sourceObj.type.toUpperCase() === 'FTP') {
              config_file = 'config/ftp_config.yaml';
            }
            const { interval, duration } = this.schedulerForm.value;
            this.api.runPipeline({ config_file, interval, duration }).subscribe({
              next: () => this.status = 'Pipeline scheduled successfully',
              error: (err) => this.status = `Error: ${err.message}`
            });
          },
          error: () => this.status = 'Error: Could not fetch source configs'
        });
      },
      error: () => this.status = 'Error: Could not fetch current config'
    });
  }
  getSelectedSourceType(): string {
    return this.sourceConfigComponent?.sourceForm?.get('type')?.value || 'API';
  }
}