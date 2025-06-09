import { Component, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { MatTabsModule } from '@angular/material/tabs';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { SourceConfig } from './source-config/source-config';
import { TargetConfig } from './target-config/target-config';
import { ConfigListComponent } from '../config-list/config-list';

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
    SourceConfig,
    TargetConfig,
    ConfigListComponent
  ]
})
export class DataExtraction {
  @ViewChild(SourceConfig) sourceConfigComponent!: SourceConfig;
  schedulerForm: FormGroup;
  status = '';

  constructor(private fb: FormBuilder, private api: ApiService) {
    this.schedulerForm = this.fb.group({
      interval: [null, [Validators.required, Validators.min(1)]],
      duration: [null, [Validators.required, Validators.min(0.1)]]
    });
  }
  runPipeline() {
    const sourceType = this.getSelectedSourceType();
    const config_file = sourceType === 'API' ? 'config/api_config.yaml' : 'config/ftp_config.yaml';
    const { interval, duration } = this.schedulerForm.value;
    this.api.runPipeline({ config_file, interval, duration }).subscribe({
      next: () => this.status = 'Pipeline scheduled successfully',
      error: (err) => this.status = `Error: ${err.message}`
    });
  }
  getSelectedSourceType(): string {
    return this.sourceConfigComponent?.sourceForm?.get('type')?.value || 'API';
  }
}