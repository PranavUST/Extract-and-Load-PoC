import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatCardModule } from '@angular/material/card';
import { ApiService } from '../../../services/api.service';

@Component({
  standalone: true,
  selector: 'app-scheduler-config',
  templateUrl: './scheduler-config.html',
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatCardModule,
    MatSelectModule
  ]
})
export class SchedulerConfig {
  private fb = inject(FormBuilder);
  private api = inject(ApiService);

  status = '';
  schedulerForm: FormGroup = this.fb.group({
    sourceType: ['', Validators.required],
    interval: [null, [Validators.required, Validators.min(1)]],
    duration: [null, [Validators.required, Validators.min(0.1)]]
  });

  runPipeline() {
    if (this.schedulerForm.valid) {
      const { sourceType, interval, duration } = this.schedulerForm.value;
      let configFile = '';
      if (sourceType === 'API') {
        configFile = 'config/api_config.yaml';
      } else if (sourceType === 'FTP') {
        configFile = 'config/ftp_config.yaml';
      }
      this.api.runPipeline({
        config_file: configFile,
        interval,
        duration
      }).subscribe({
        next: () => this.status = 'Pipeline scheduled successfully',
        error: (err) => this.status = `Error: ${err.message}`
      });
    }
  }
  stopPipeline() {
    this.api.stopPipeline().subscribe({
      next: () => this.status = 'Pipeline stopped',
      error: (err: any) => this.status = `Error: ${err.message}`
    });
  }
}