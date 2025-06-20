// config-list.ts (CORRECTED)
import { Component, OnInit, ViewChild, TemplateRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { HttpClient } from '@angular/common/http';
import { EditSourceConfigDialogComponent } from './edit-source-config-dialog';
import { EditTargetConfigDialogComponent } from './edit-target-config-dialog';
import { MatDialog } from '@angular/material/dialog';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { ReactiveFormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatExpansionModule } from '@angular/material/expansion';

// Define interfaces for type safety
export interface SourceConfig {
  name: string;
  type: string;
  endpoint?: string;
  authToken?: string;
  ftpHost?: string;
  ftpUsername?: string;
  ftpPassword?: string;
  retries?: number;
  advanced?: {
    apiLimit?: number;
    apiMaxPages?: number;
    ftpRemoteDir?: string;
    ftpLocalDir?: string;
    ftpFileTypes?: string;
    ftpRetryDelay?: number;
    csvOutputPath?: string;
  };
  apiLimit?: number;
  apiMaxPages?: number;
  ftpRemoteDir?: string;
  ftpLocalDir?: string;
  ftpFileTypes?: string;
  ftpRetryDelay?: number;
  csvOutputPath?: string;
}

interface TargetConfig {
  name: string;
  tableName?: string;
  type?: string;
  advanced?: {
    apiLimit?: number;
    apiMaxPages?: number;
    ftpRemoteDir?: string;
    ftpLocalDir?: string;
    ftpFileTypes?: string;
    ftpRetryDelay?: number;
    csvOutputPath?: string;
  };
  apiLimit?: number;
  apiMaxPages?: number;
  ftpRemoteDir?: string;
  ftpLocalDir?: string;
  ftpFileTypes?: string;
  ftpRetryDelay?: number;
  csvOutputPath?: string;
}

@Component({
  standalone: true,
  selector: 'app-config-list',
  templateUrl: './config-list.html',
  styleUrls: ['./config-list.scss'],
  imports: [
    CommonModule,
    MatCardModule,
    MatTableModule,
    MatButtonModule,
    MatListModule,
    MatIconModule,
    EditSourceConfigDialogComponent,
    EditTargetConfigDialogComponent,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatExpansionModule
  ]
})
export class ConfigListComponent implements OnInit {
  sourceConfigs: SourceConfig[] = [];
  targetConfigs: TargetConfig[] = [];
  currentSource: string | null = null;
  currentTarget: string | null = null;
  editForm: FormGroup;
  // Inline editing state
  editingSourceConfig: SourceConfig | null = null;
  editingTargetConfig: TargetConfig | null = null;
  editSourceFormGroup: FormGroup;
  editTargetFormGroup: FormGroup;
  @ViewChild('editSourceDialog') editSourceDialog!: TemplateRef<any>;
  editingConfig: any = null;
  isTargetEditFormReady = false;

  constructor(private http: HttpClient, private dialog: MatDialog, private fb: FormBuilder, private api: ApiService) {
    this.editForm = this.fb.group({
      name: ['', Validators.required],
      type: ['API', Validators.required],
      endpoint: [''],
      authToken: [''],
      ftpHost: [''],
      ftpUsername: [''],
      ftpPassword: [''],
      retries: [3],
      // Advanced fields
      apiLimit: [100],
      apiMaxPages: [10],
      ftpRemoteDir: [''],
      ftpLocalDir: [''],
      ftpFileTypes: ['.csv,.json,.parquet'],
      ftpRetryDelay: [5],
      csvOutputPath: ['data/output.csv']
    });
    // Inline edit forms
    this.editSourceFormGroup = this.fb.group({
      name: ['', Validators.required],
      type: ['API', Validators.required],
      endpoint: [''],
      authToken: [''],
      ftpHost: [''],
      ftpUsername: [''],
      ftpPassword: [''],
      retries: [3],
      apiLimit: [100],
      apiMaxPages: [10],
      ftpRemoteDir: [''],
      ftpLocalDir: [''],
      ftpFileTypes: ['.csv,.json,.parquet'],
      ftpRetryDelay: [5],
      csvOutputPath: ['data/output.csv']
    });
    this.editTargetFormGroup = this.fb.group({
      name: ['', Validators.required],
      type: ['DATABASE', Validators.required],
      tableName: [''],
      apiLimit: [100],
      apiMaxPages: [10],
      ftpRemoteDir: [''],
      ftpLocalDir: [''],
      ftpFileTypes: ['.csv,.json,.parquet'],
      ftpRetryDelay: [5],
      csvOutputPath: ['data/output.csv']
    });
  }

  ngOnInit(): void {
    this.loadSourceConfigs();
    this.loadTargetConfigs();
    this.loadCurrentConfig();
  }

  private loadSourceConfigs(): void {
    // Remove /api prefix to match your Flask server endpoints
    this.http.get<SourceConfig[]>('http://localhost:5000/saved-source-configs').subscribe({
      next: (data) => this.sourceConfigs = data || [],
      error: (error) => {
        console.error('Error loading source configs:', error);
        this.sourceConfigs = [];
      }
    });
  }

  private loadTargetConfigs(): void {
    // Remove /api prefix to match your Flask server endpoints
    this.http.get<TargetConfig[]>('http://localhost:5000/saved-target-configs').subscribe({
      next: (data) => this.targetConfigs = data || [],
      error: (error) => {
        console.error('Error loading target configs:', error);
        this.targetConfigs = [];
      }
    });
  }
  loadCurrentConfig() {
    this.http.get<{source: string, target: string}>('http://localhost:5000/current-config').subscribe({
      next: (data) => {
        this.currentSource = data.source;
        this.currentTarget = data.target;
      }
    });
  }
  setCurrentSource(name: string) {
    this.http.post('http://localhost:5000/current-config', { source: name.trim(), target: this.currentTarget }).subscribe(() => {
      this.currentSource = name.trim();
    });
  }

  setCurrentTarget(name: string) {
    this.http.post('http://localhost:5000/current-config', { source: this.currentSource, target: name.trim() }).subscribe(() => {
      this.currentTarget = name.trim();
    });
  }
  deleteSourceConfig(config: SourceConfig) {
    if (confirm(`Delete source config "${config.name}"?`)) {
      this.http.delete(`http://localhost:5000/saved-source-configs/${config.name}`).subscribe({
        next: () => {
          this.loadSourceConfigs();
          this.loadCurrentConfig(); // <-- Add this line
        },
        error: (err) => alert('Delete failed: ' + err.message)
      });
    }
  } 
  editSourceConfig(config: SourceConfig) {
    // Patch: always return a valid dialogRef for tests
    const dialogRef = this.dialog.open(EditSourceConfigDialogComponent, {
      width: '400px',
      data: { ...config }
    });
    // Defensive: check dialogRef and afterClosed
    if (!dialogRef || typeof dialogRef.afterClosed !== 'function') {
      throw new Error('DialogRef mock missing afterClosed');
    }
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        // Send PUT/PATCH request to update config
        this.http.put(`http://localhost:5000/saved-source-configs/${config.name}`, result).subscribe({
          next: () => this.loadSourceConfigs(),
          error: (err) => alert('Update failed: ' + err.message)
        });
      }
    });
  }
  deleteTargetConfig(config: TargetConfig) {
    if (confirm(`Delete target config "${config.name}"?`)) {
      this.http.delete(`http://localhost:5000/saved-target-configs/${config.name}`).subscribe({
        next: () => {
          this.loadTargetConfigs();
          this.loadCurrentConfig(); // <-- Add this line
        },
        error: (err) => alert('Delete failed: ' + err.message)
      });
    }
  }
  editTargetConfig(config: TargetConfig) {
    // Patch: always return a valid dialogRef for tests
    const dialogRef = this.dialog.open(EditTargetConfigDialogComponent, {
      width: '400px',
      data: { ...config }
    });
    if (!dialogRef || typeof dialogRef.afterClosed !== 'function') {
      throw new Error('DialogRef mock missing afterClosed');
    }
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.http.put(`http://localhost:5000/saved-target-configs/${config.name}`, result).subscribe({
          next: () => this.loadTargetConfigs(),
          error: (err) => alert('Update failed: ' + err.message)
        });
      }
    });
  }

    // Add to config-list.ts
  debugConfigs() {
    console.log('=== CONFIGURATION DEBUG ===');
    console.log('Current Source:', this.currentSource);
    console.log('Current Target:', this.currentTarget);
    console.log('Available Sources:', this.sourceConfigs);
    console.log('Available Targets:', this.targetConfigs);
    
    // Check backend config files
    this.http.get('http://localhost:5000/debug-configs').subscribe({
      next: (data) => console.log('Backend configs:', data),
      error: (err) => console.error('Debug failed:', err)
    });
  }

  openEditSourceDialog(config: any) {
    // Use the component dialog, not a template
    this.dialog.open(EditSourceConfigDialogComponent, {
      data: { ...config },
      minWidth: '700px',
      maxWidth: '1100px',
      width: '900px',
      panelClass: 'edit-source-dialog-panel'
    }).afterClosed().subscribe(() => {
      this.loadSourceConfigs();
      this.loadCurrentConfig();
    });
  }

  // Add this method if it doesn't exist
  loadConfigs() {
    // Implement logic to reload configs, e.g.:
    // this.api.getSourceConfigs().subscribe(configs => this.configs = configs);
    // ...or trigger however you normally reload the list...
  }

  saveEdit(dialogRef: any) {
    if (this.editForm.valid) {
      const form = this.editForm.value;
      const payload = {
        name: form.name,
        type: form.type,
        endpoint: form.endpoint,
        authToken: form.authToken,
        ftpHost: form.ftpHost,
        ftpUsername: form.ftpUsername,
        ftpPassword: form.ftpPassword,
        retries: form.retries,
        advanced: {
          apiLimit: form.apiLimit,
          apiMaxPages: form.apiMaxPages,
          ftpRemoteDir: form.ftpRemoteDir,
          ftpLocalDir: form.ftpLocalDir,
          ftpFileTypes: form.ftpFileTypes,
          ftpRetryDelay: form.ftpRetryDelay,
          csvOutputPath: form.csvOutputPath
        }
      };
      this.api.saveSourceConfig(payload).subscribe({
        next: () => {
          dialogRef.close();
          this.loadConfigs(); // Use the correct method to reload configs
        },
        error: (err: any) => alert('Save failed: ' + err.message)
      });
    }
  }

  // Inline edit logic for source configs
  startEditSourceConfig(config: SourceConfig) {
    this.editingSourceConfig = config;
    this.editSourceFormGroup.patchValue({
      name: config.name || '',
      type: config.type || 'API',
      endpoint: config.endpoint || '',
      authToken: config.authToken || '',
      ftpHost: config.ftpHost || '',
      ftpUsername: config.ftpUsername || '',
      ftpPassword: config.ftpPassword || '',
      retries: config.retries ?? 3,
      apiLimit: (config.advanced?.apiLimit ?? config.apiLimit) ?? 100,
      apiMaxPages: (config.advanced?.apiMaxPages ?? config.apiMaxPages) ?? 10,
      ftpRemoteDir: (config.advanced?.ftpRemoteDir ?? config.ftpRemoteDir) ?? '',
      ftpLocalDir: (config.advanced?.ftpLocalDir ?? config.ftpLocalDir) ?? '',
      ftpFileTypes: (config.advanced?.ftpFileTypes ?? config.ftpFileTypes) ?? '.csv,.json,.parquet',
      ftpRetryDelay: (config.advanced?.ftpRetryDelay ?? config.ftpRetryDelay) ?? 5,
      csvOutputPath: (config.advanced?.csvOutputPath ?? config.csvOutputPath) ?? 'data/output.csv'
    });
  }

  cancelEditSourceConfig() {
    this.editingSourceConfig = null;
  }

  saveEditSourceConfig() {
    if (this.editSourceFormGroup.valid && this.editingSourceConfig) {
      const form = this.editSourceFormGroup.value;
      const payload = {
        name: form.name,
        type: form.type,
        endpoint: form.endpoint,
        authToken: form.authToken,
        ftpHost: form.ftpHost,
        ftpUsername: form.ftpUsername,
        ftpPassword: form.ftpPassword,
        retries: form.retries,
        advanced: {
          apiLimit: form.apiLimit,
          apiMaxPages: form.apiMaxPages,
          ftpRemoteDir: form.ftpRemoteDir,
          ftpLocalDir: form.ftpLocalDir,
          ftpFileTypes: form.ftpFileTypes,
          ftpRetryDelay: form.ftpRetryDelay,
          csvOutputPath: form.csvOutputPath
        }
      };
      this.http.put(`http://localhost:5000/saved-source-configs/${this.editingSourceConfig.name}`, payload).subscribe({
        next: () => {
          this.editingSourceConfig = null;
          this.loadSourceConfigs();
          this.loadCurrentConfig();
        },
        error: (err) => alert('Update failed: ' + err.message)
      });
    }
  }

  // Inline edit logic for target configs
  startEditTargetConfig(config: TargetConfig) {
    this.isTargetEditFormReady = false;
    this.editingTargetConfig = config;
    this.editTargetFormGroup.patchValue({
      name: config.name || '',
      type: 'DATABASE',
      tableName: config.tableName || '',
      apiLimit: (config.advanced?.apiLimit ?? config.apiLimit) ?? 100,
      apiMaxPages: (config.advanced?.apiMaxPages ?? config.apiMaxPages) ?? 10,
      ftpRemoteDir: (config.advanced?.ftpRemoteDir ?? config.ftpRemoteDir) ?? '',
      ftpLocalDir: (config.advanced?.ftpLocalDir ?? config.ftpLocalDir) ?? '',
      ftpFileTypes: (config.advanced?.ftpFileTypes ?? config.ftpFileTypes) ?? '.csv,.json,.parquet',
      ftpRetryDelay: (config.advanced?.ftpRetryDelay ?? config.ftpRetryDelay) ?? 5,
      csvOutputPath: (config.advanced?.csvOutputPath ?? config.csvOutputPath) ?? 'data/output.csv'
    });
    // Ensure form is ready after patching
    Promise.resolve().then(() => this.isTargetEditFormReady = true);
  }

  cancelEditTargetConfig() {
    this.editingTargetConfig = null;
    this.isTargetEditFormReady = false;
  }

  saveEditTargetConfig() {
    if (this.editTargetFormGroup.valid && this.editingTargetConfig) {
      const form = this.editTargetFormGroup.value;
      const payload = {
        name: form.name,
        type: form.type,
        tableName: form.tableName,
        advanced: {
          apiLimit: form.apiLimit,
          apiMaxPages: form.apiMaxPages,
          ftpRemoteDir: form.ftpRemoteDir,
          ftpLocalDir: form.ftpLocalDir,
          ftpFileTypes: form.ftpFileTypes,
          ftpRetryDelay: form.ftpRetryDelay,
          csvOutputPath: form.csvOutputPath
        }
      };
      this.http.put(`http://localhost:5000/saved-target-configs/${this.editingTargetConfig.name}`, payload).subscribe({
        next: () => {
          this.editingTargetConfig = null;
          this.isTargetEditFormReady = false;
          this.loadTargetConfigs();
          this.loadCurrentConfig();
        },
        error: (err) => alert('Update failed: ' + err.message)
      });
    }
  }
}