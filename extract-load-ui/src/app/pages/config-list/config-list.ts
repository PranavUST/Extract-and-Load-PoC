// config-list.ts (CORRECTED)
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { HttpClient } from '@angular/common/http';
import { MatDialog } from '@angular/material/dialog';
// Define interfaces for type safety
interface SourceConfig {
  name: string;
  type: string;
  endpoint?: string;
  authToken?: string;
  ftpHost?: string;
  ftpUsername?: string;
  retries?: number;
}

interface TargetConfig {
  name: string;
  tableName: string;
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
    MatIconModule
  ]
})
export class ConfigListComponent implements OnInit {
  sourceConfigs: SourceConfig[] = [];
  targetConfigs: TargetConfig[] = [];

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.loadSourceConfigs();
    this.loadTargetConfigs();
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
  deleteSourceConfig(config: SourceConfig) {
    if (confirm(`Delete source config "${config.name}"?`)) {
      // Call your API to delete, then reload the list
      this.http.delete(`http://localhost:5000/saved-source-configs/${config.name}`).subscribe({
        next: () => this.loadSourceConfigs(),
        error: (err) => alert('Delete failed: ' + err.message)
      });
    }
  }
  editSourceConfig(config: SourceConfig) {
    // You can open a dialog with a form, or navigate to an edit page
    alert('Edit not implemented yet for: ' + config.name);
    // Or implement your edit logic here
  }
  deleteTargetConfig(config: TargetConfig) {
    if (confirm(`Delete target config "${config.name}"?`)) {
      this.http.delete(`http://localhost:5000/saved-target-configs/${config.name}`).subscribe({
        next: () => this.loadTargetConfigs(),
        error: (err) => alert('Delete failed: ' + err.message)
      });
    }
  }
  editTargetConfig(config: TargetConfig) {
    alert('Edit not implemented yet for: ' + config.name);
    // Implement edit logic here
  }
}