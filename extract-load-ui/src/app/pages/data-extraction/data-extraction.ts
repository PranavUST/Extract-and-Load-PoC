import { Component, OnInit, OnDestroy, ViewChild } from '@angular/core';
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
export class DataExtraction implements OnInit, OnDestroy {
  @ViewChild(SourceConfig) sourceConfigComponent!: SourceConfig;
  schedulerForm: FormGroup;
  status = '';
  statusDetails: {timestamp: string, message: string}[] = [];
  private pollInterval: any;
  ngOnInit() {
    // Fetch the latest scheduled runId on load
    this.fetchLatestScheduledRunId();
    // Start polling for status if runId exists
    setTimeout(() => {
      if (this.runId) {
        this.pollStatus();
      }
    }, 500);
  }
  ngOnDestroy() {
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
    }
  }
  startScheduledPolling() {
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
      this.pollInterval = null;
    }
    this.statusDetails = [];
    this.runId = '';
    // Poll for run_id every 2 seconds until found, then start status polling
    const runIdInterval = setInterval(() => {
      this.http.get<{run_id: string}>('http://localhost:5000/latest-scheduled-run-id').subscribe({
        next: (res) => {
          console.log('Fetched run_id:', res.run_id);
          if (res.run_id) {
            this.runId = res.run_id;
            clearInterval(runIdInterval);
            this.pollStatus(); // Start polling for status only after runId is available
          }
        }
      });
    }, 2000);
  }
  pollStatus() {
    // Clear any previous polling intervals
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
      this.pollInterval = null;
    }
    this.pollInterval = setInterval(() => {
      if (!this.runId) {
        this.statusDetails = [];
        return;
      }
      this.http.get<{status: {timestamp: string, message: string}[]}>(
        `http://localhost:5000/pipeline-status?run_id=${this.runId}`
      ).subscribe({
        next: (res) => this.statusDetails = res.status,
        error: () => this.statusDetails = []
      });
    }, 2000);
  }

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
            if (!current.source || !sourceObj) {
              this.status = 'Error: No valid source config selected. Please select or create a source config.';
              return;
            }
            let config_file = 'config/api_config.yaml'; // default
            if (sourceObj.type && sourceObj.type.toUpperCase() === 'FTP') {
              config_file = 'config/ftp_config.yaml';
            }
            const { interval, duration } = this.schedulerForm.value;
            this.api.runPipeline({ config_file, interval, duration }).subscribe({
              next: () => {
                this.status = 'Pipeline scheduled successfully',
                this.startScheduledPolling();
              },
              error: (err) => this.status = `Error: ${err.message}`
            });
          },
          error: () => this.status = 'Error: Could not fetch source configs'
        });
      },
      error: () => this.status = 'Error: Could not fetch current config'
    });
  }
  runId: string = ''; 
  runPipelineOnce() {
    this.http.get<{source: string, target: string}>('http://localhost:5000/current-config').subscribe({
      next: (current) => {
        this.http.get<any[]>('http://localhost:5000/saved-source-configs').subscribe({
          next: (sources) => {
            const sourceObj = sources.find(s => s.name === current.source);
            if (!current.source || !sourceObj) {
              this.status = 'Error: No valid source config selected. Please select or create a source config.';
              return;
            }
            let config_file = 'config/api_config.yaml';
            if (sourceObj.type && sourceObj.type.toUpperCase() === 'FTP') {
              config_file = 'config/ftp_config.yaml';
            }
            this.http.post<{status: string, run_id: string}>('http://localhost:5000/run-pipeline-once', { config_file }).subscribe({
              next: (res) => {
                this.status = 'Pipeline started (run once)';
                this.runId = res.run_id; // Save run_id for polling
                this.pollStatus();
              },
              error: (err) => this.status = `Error: ${err.message}`
            });
          },
          error: () => this.status = 'Error: Could not fetch source configs'
        });
      },
      error: () => this.status = 'Error: Could not fetch current config'
    });
  }
  fetchLatestScheduledRunId() {
    this.http.get<{run_id: string}>('http://localhost:5000/latest-scheduled-run-id').subscribe({
      next: (res) => {
        if (res.run_id) {
          this.runId = res.run_id;
        }
      }
    });
  }
  stopPipeline() {
    this.api.stopPipeline().subscribe({
      next: () => this.status = 'Pipeline stopped',
      error: (err) => this.status = `Error: ${err.error?.message || err.message || 'Failed to stop pipeline'}`
    });
  }
  getSelectedSourceType(): string {
    return this.sourceConfigComponent?.sourceForm?.get('type')?.value || 'API';
  }
}