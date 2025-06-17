import { Component, OnInit, OnDestroy, AfterViewInit, ViewChild } from '@angular/core';
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
import { MatDividerModule } from '@angular/material/divider';
import { ReloadService } from '../../services/reload.service';
import { FormControl } from '@angular/forms';
import { MatSelectModule } from '@angular/material/select';
import { MatOptionModule } from '@angular/material/core';
import { MatExpansionModule } from '@angular/material/expansion';
import { Subscription } from 'rxjs';
@Component({
  standalone: true,
  selector: 'app-data-extraction',
  templateUrl: './data-extraction.html',
  styleUrls: ['./data-extraction.scss'],
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatTabsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatDividerModule,
    RouterModule,
    SourceConfig,
    TargetConfig,
    ConfigListComponent,
    MatSelectModule,
    MatOptionModule,
    MatExpansionModule
  ]
})
export class DataExtraction implements OnInit, OnDestroy, AfterViewInit {
  @ViewChild(ConfigListComponent) configList!: ConfigListComponent;
  @ViewChild('sourceConfigComp', { static: false }) sourceConfigComp: any;
  schedulerForm: FormGroup;
  status = '';
  runIdPollInterval: any;
  latestPolledRunId: string = '';
  statusDetails: {timestamp: string, message: string}[] = [];
  private pollInterval: any;
  waitingForScheduledRun: boolean = false;
  isRunOnceDisabled = false;
  advancedForm: FormGroup;
  selectedSourceType: 'API' | 'FTP' = 'API';
  configSub?: any; // Add definite assignment assertion or make it optional

  editingConfig: any = null;
  editConfigForm: FormGroup;

  ngOnInit() {
    this.startRunIdPolling();
    this.refreshSourceType();
  }

  ngAfterViewInit() {
    // Try to get the SourceConfig component and subscribe to its type changes
    // Assumes <app-source-config #sourceConfigComp> in template
    setTimeout(() => {
      if (this.sourceConfigComp && this.sourceConfigComp.sourceForm) {
        const typeCtrl = this.sourceConfigComp.sourceForm.get('type');
        if (typeCtrl) {
          this.selectedSourceType = (typeCtrl.value || '').toUpperCase() === 'FTP' ? 'FTP' : 'API';
          typeCtrl.valueChanges.subscribe((type: string) => {
            this.selectedSourceType = (type || '').toUpperCase() === 'FTP' ? 'FTP' : 'API';
            this.refreshAdvancedFields();
          });
        }
      }
    }, 0);
  }

  refreshSourceType() {
    // Always fetch the latest current config and saved source configs
    this.http.get<{source: string}>('http://localhost:5000/current-config').subscribe({
      next: (current) => {
        if (!current.source) {
          this.selectedSourceType = 'API'; // fallback
          this.refreshAdvancedFields();
          return;
        }
        this.http.get<any[]>('http://localhost:5000/saved-source-configs').subscribe({
          next: (sources) => {
            const sourceObj = sources.find(
              s => (s.name || '').trim() === (current.source || '').trim()
            );
            if (sourceObj && typeof sourceObj.type === 'string') {
              const type = (sourceObj.type || '').toUpperCase();
              this.selectedSourceType = type === 'FTP' ? 'FTP' : 'API';
            } else {
              this.selectedSourceType = 'API';
            }
            this.refreshAdvancedFields();
          },
          error: () => {
            this.selectedSourceType = 'API';
            this.refreshAdvancedFields();
          }
        });
      },
      error: () => {
        this.selectedSourceType = 'API';
        this.refreshAdvancedFields();
      }
    });
  }
  refreshConfigs() {
    this.reloadService.reload();
    this.refreshSourceType(); // Also update source type and advanced fields when configs change
  }
  refreshAdvancedFields() {
    // Reset advanced fields based on selectedSourceType
    if (this.selectedSourceType === 'API') {
      this.advancedForm.patchValue({
        apiLimit: 100,
        apiMaxPages: 10,
        // ...other API defaults if needed...
      });
    } else if (this.selectedSourceType === 'FTP') {
      this.advancedForm.patchValue({
        ftpRemoteDir: '',
        ftpLocalDir: '',
        ftpFileTypes: '.csv,.json,.parquet',
        ftpRetryDelay: 5,
        // ...other FTP defaults if needed...
      });
    }
    // Always keep CSV/DB fields as is or set defaults if needed
  }
  ngOnDestroy() {
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
    }
    if (this.runIdPollInterval) {
      clearInterval(this.runIdPollInterval);
    }
    if (this.configSub) this.configSub.unsubscribe();
  }
  startRunIdPolling() {
    if (this.runIdPollInterval) {
      clearInterval(this.runIdPollInterval);
    }
    this.runIdPollInterval = setInterval(() => {
      this.http.get<{run_id: string}>('http://localhost:5000/latest-scheduled-run-id').subscribe({
        next: (res) => {
          if (res.run_id && res.run_id !== this.latestPolledRunId) {
            this.latestPolledRunId = res.run_id;
            this.runId = res.run_id;
            this.waitingForScheduledRun = false;
            this.pollStatus(); // Start polling for logs for the new run
          } else if (!res.run_id) {
            this.waitingForScheduledRun = true;
          }
        },
        error: () => {
          this.waitingForScheduledRun = true;
        }
      });
    }, 5000); // Poll every 5 seconds
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
        next: (res) => {
          console.log('Pipeline status response:', res);
          this.statusDetails = res.status;
          if (this.statusDetails.some(s => s.message.includes('Pipeline completed successfully'))) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
          }
        },
        error: () => this.statusDetails = []
      });
    }, 2000);
  }

  constructor(private fb: FormBuilder, private api: ApiService, private http: HttpClient, private reloadService: ReloadService) {
    this.schedulerForm = this.fb.group({
      interval: [null, [Validators.required, Validators.min(1)]],
      duration: [null, [Validators.required, Validators.min(0.1)]]
    });
    this.advancedForm = this.fb.group({
      apiLimit: [100],
      apiMaxPages: [10],
      ftpRemoteDir: [''],
      ftpLocalDir: [''],
      ftpFileTypes: ['.csv,.json,.parquet'],
      ftpRetryDelay: [5],
      csvOutputPath: ['data/output.csv']
      // dbEnabled: [true] // Removed
    });
    this.editConfigForm = this.fb.group({
      type: ['API', Validators.required],
      apiLimit: [100],
      apiMaxPages: [10],
      ftpRemoteDir: [''],
      ftpLocalDir: [''],
      ftpFileTypes: ['.csv,.json,.parquet'],
      ftpRetryDelay: [5],
      csvOutputPath: ['data/output.csv']
    });
  }
  runPipeline() {
    // Always get the current config from backend
    this.http.get<{source: string, target: string}>('http://localhost:5000/current-config').subscribe({
      next: (current) => {
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
                this.status = 'Pipeline scheduled successfully';
                this.startRunIdPolling();
                // No need to call startScheduledPolling or pollStatus here
              },
              error: (err) => {
                this.status = `Error: ${err.error?.message || err.message || 'Failed to schedule pipeline'}`;
              }
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
    this.isRunOnceDisabled = true;
    this.http.get<{source: string, target: string}>('http://localhost:5000/current-config').subscribe({
      next: (current) => {
        this.http.get<any[]>('http://localhost:5000/saved-source-configs').subscribe({
          next: (sources) => {
            const sourceObj = sources.find(s => s.name === current.source);
            if (!current.source || !sourceObj) {
              this.status = 'Error: No valid source config selected. Please select or create a source config.';
              this.isRunOnceDisabled = false;
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
                // Do not re-enable until stopped
              },
              error: (err) => {
                this.status = `Error: ${err.message}`;
                this.isRunOnceDisabled = false;
              }
            });
          },
          error: () => {
            this.status = 'Error: Could not fetch source configs';
            this.isRunOnceDisabled = false;
          }
        });
      },
      error: () => {
        this.status = 'Error: Could not fetch current config';
        this.isRunOnceDisabled = false;
      }
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
    // Stop polling for runId and logs
    if (this.runIdPollInterval) {
      clearInterval(this.runIdPollInterval);
      this.runIdPollInterval = null;
    }
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
      this.pollInterval = null;
    }
    this.status = 'Pipeline stopped';
    // Optionally clear logs and runId
    this.statusDetails = [];
    this.runId = '';
    this.waitingForScheduledRun = false;
    this.isRunOnceDisabled = false;

    // Call backend to stop scheduler
    this.api.stopPipeline().subscribe({
      next: () => {},
      error: (err) => this.status = `Error: ${err.error?.message || err.message || 'Failed to stop pipeline'}`
    });
  }

  onEditConfig(config: any) {
    this.editingConfig = config;
    this.editConfigForm.patchValue({
      type: config.type || 'API',
      apiLimit: config.advanced?.apiLimit ?? 100,
      apiMaxPages: config.advanced?.apiMaxPages ?? 10,
      ftpRemoteDir: config.advanced?.ftpRemoteDir ?? '',
      ftpLocalDir: config.advanced?.ftpLocalDir ?? '',
      ftpFileTypes: config.advanced?.ftpFileTypes ?? '.csv,.json,.parquet',
      ftpRetryDelay: config.advanced?.ftpRetryDelay ?? 5,
      csvOutputPath: config.advanced?.csvOutputPath ?? 'data/output.csv'
    });
  }

  saveEditedConfig() {
    if (this.editConfigForm.valid && this.editingConfig) {
      const adv = this.editConfigForm.value;
      const payload = {
        ...this.editingConfig,
        advanced: {
          apiLimit: adv.apiLimit,
          apiMaxPages: adv.apiMaxPages,
          ftpRemoteDir: adv.ftpRemoteDir,
          ftpLocalDir: adv.ftpLocalDir,
          ftpFileTypes: adv.ftpFileTypes,
          ftpRetryDelay: adv.ftpRetryDelay,
          csvOutputPath: adv.csvOutputPath
        }
      };
      this.api.saveSourceConfig(payload).subscribe({
        next: () => {
          this.editingConfig = null;
          this.refreshConfigs();
        },
        error: (err) => alert('Save failed: ' + err.message)
      });
    }
  }

  cancelEditConfig() {
    this.editingConfig = null;
  }
}