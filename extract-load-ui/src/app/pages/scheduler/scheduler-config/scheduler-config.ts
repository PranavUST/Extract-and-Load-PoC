import { Component, inject, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatCardModule } from '@angular/material/card';
import { ApiService } from '../../../services/api.service';
import { Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';

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
export class SchedulerConfig implements OnDestroy {
  private fb = inject(FormBuilder);
  private api = inject(ApiService);
  private http = inject(HttpClient);

  status = '';
  isRunOnceDisabled = false;
  schedulerForm: FormGroup = this.fb.group({
    scheduleType: ['interval', Validators.required],
    interval: [null],
    daysOfMonth: [''],
    duration: [null]
  });
  statusDetails: {timestamp: string, message: string}[] = [];
  pollInterval: any;
  runId: string = '';

  onScheduleTypeChange(type: string) {
    // Reset validators based on type
    if (type === 'interval' || type === 'hourly') {
      this.schedulerForm.get('duration')?.setValidators([Validators.required, Validators.min(0.1)]);
    } else {
      this.schedulerForm.get('duration')?.clearValidators();
    }
    if (type === 'interval') {
      this.schedulerForm.get('interval')?.setValidators([Validators.required, Validators.min(1)]);
      this.schedulerForm.get('daysOfMonth')?.clearValidators();
    } else if (type === 'daysOfMonth') {
      this.schedulerForm.get('interval')?.clearValidators();
      this.schedulerForm.get('daysOfMonth')?.setValidators([Validators.required, Validators.pattern(/^\s*\d{1,2}(\s*,\s*\d{1,2})*\s*$/)]);
    } else {
      this.schedulerForm.get('interval')?.clearValidators();
      this.schedulerForm.get('daysOfMonth')?.clearValidators();
    }
    this.schedulerForm.get('interval')?.updateValueAndValidity();
    this.schedulerForm.get('daysOfMonth')?.updateValueAndValidity();
    this.schedulerForm.get('duration')?.updateValueAndValidity();
  }

  runPipeline() {
    if (this.schedulerForm.valid) {
      const { scheduleType, interval, daysOfMonth, duration } = this.schedulerForm.value;
      this.api.getCurrentConfig().subscribe({
        next: (currentConfig) => {
          const sourceName = currentConfig.source;
          this.api.getSourceConfigs().subscribe({
            next: (sources: any[]) => {
              const source = sources.find((s: any) => s.name === sourceName);
              let configFile = 'config/api_config.yaml';
              if (source && source.type && source.type.toUpperCase() === 'FTP') {
                configFile = 'config/ftp_config.yaml';
              }
              this.api.runPipeline({
                config_file: configFile,
                scheduleType,
                interval,
                daysOfMonth,
                duration
              }).subscribe({
                next: (res) => {
                  this.status = 'Pipeline scheduled successfully';
                  this.fetchLatestScheduledRunId();
                },
                error: (err) => this.status = `Error: ${err.error?.message || err.message || 'Failed to schedule pipeline'}`
              });
            },
            error: () => this.status = 'Error: Could not fetch source configs'
          });
        },
        error: () => this.status = 'Error: Could not fetch current config'
      });
    }
  }
  stopPipeline() {
    this.api.stopPipeline().subscribe({
      next: () => this.status = 'Pipeline stopped',
      error: (err: any) => this.status = `Error: ${err.message}`
    });
  }
  runOnce() {
    this.isRunOnceDisabled = true;
    this.api.getCurrentConfig().subscribe({
      next: (currentConfig) => {
        const sourceName = currentConfig.source;
        this.api.getSourceConfigs().subscribe({
          next: (sources: any[]) => {
            const source = sources.find((s: any) => s.name === sourceName);
            let configFile = 'config/api_config.yaml';
            if (source && source.type && source.type.toUpperCase() === 'FTP') {
              configFile = 'config/ftp_config.yaml';
            }
            this.api.runPipelineOnce({ config_file: configFile }).subscribe({
              next: (res) => {
                this.status = 'Pipeline run once successfully';
                this.runId = res.run_id;
                this.pollStatus();
              },
              error: (err: any) => this.status = `Error: ${err.message}`
            });
          },
          error: () => this.status = 'Error: Could not fetch source configs'
        });
      },
      error: () => this.status = 'Error: Could not fetch current config'
    });
  }

  fetchLatestScheduledRunId() {
    this.api.getLatestScheduledRunId().subscribe({
      next: (res) => {
        if (res.run_id) {
          this.runId = res.run_id;
          this.pollStatus();
        }
      }
    });
  }

  pollStatus() {
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
    }
    if (!this.runId) return;
    this.pollInterval = setInterval(() => {
      this.api.getPipelineStatusByRunId(this.runId).subscribe({
        next: (res) => {
          this.statusDetails = res.status;
          if (this.statusDetails.some(s => s.message.includes('Pipeline completed successfully'))) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
          }
        },
        error: () => this.statusDetails = []
      });
    }, 5000);
  }

  ngOnDestroy() {
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
    }
  }

  getSourceConfigs(): Observable<any[]> {
    return this.api.getSourceConfigs();
  }
  getCurrentConfigFile(): string {
    // Remove Node.js require usage; use Angular HttpClient to fetch config from backend
    // This logic should be moved to the ApiService and use getCurrentConfig() and getSourceConfigs() methods
    // Example:
    // this.apiService.getCurrentConfig().subscribe(currentConfig => {
    //   this.apiService.getSourceConfigs().subscribe(savedSources => {
    //     const sourceName = currentConfig.source;
    //     const source = savedSources.find((s: any) => s.name === sourceName);
    //     if (source && source.type && source.type.toUpperCase() === 'FTP') {
    //       // Use FTP config
    //     } else {
    //       // Use API config
    //     }
    //   });
    // });
    return 'config/api_config.yaml';
  }
}