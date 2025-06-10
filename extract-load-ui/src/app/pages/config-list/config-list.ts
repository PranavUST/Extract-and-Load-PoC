// config-list.ts (CORRECTED)
import { Component, OnInit } from '@angular/core';
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
}

interface TargetConfig {
  name: string;
  tableName?: string;
  type?: string;
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
    EditTargetConfigDialogComponent
  ]
})
export class ConfigListComponent implements OnInit {
  sourceConfigs: SourceConfig[] = [];
  targetConfigs: TargetConfig[] = [];
  currentSource: string | null = null;
  currentTarget: string | null = null;

  constructor(private http: HttpClient, private dialog: MatDialog) {}

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
    this.http.post('http://localhost:5000/current-config', { source: name, target: this.currentTarget }).subscribe(() => {
      this.currentSource = name;
    });
  }

  setCurrentTarget(name: string) {
    this.http.post('http://localhost:5000/current-config', { source: this.currentSource, target: name }).subscribe(() => {
      this.currentTarget = name;
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
    const dialogRef = this.dialog.open(EditSourceConfigDialogComponent, {
      width: '400px',
      data: { ...config }
    });
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
    const dialogRef = this.dialog.open(EditTargetConfigDialogComponent, {
      width: '400px',
      data: { ...config }
    });
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.http.put(`http://localhost:5000/saved-target-configs/${config.name}`, result).subscribe({
          next: () => this.loadTargetConfigs(),
          error: (err) => alert('Update failed: ' + err.message)
        });
      }
    });
  }
}