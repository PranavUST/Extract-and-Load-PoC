// config-list.ts (CORRECTED)
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatListModule } from '@angular/material/list';
import { HttpClient } from '@angular/common/http';

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
    MatListModule
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
}