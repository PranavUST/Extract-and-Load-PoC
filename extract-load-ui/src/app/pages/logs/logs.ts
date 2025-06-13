import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { LogService } from './log.service';

@Component({
  standalone: true,
  selector: 'app-logs',
  templateUrl: './logs.html',
  styleUrls: ['./logs.scss'],
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule
  ]
})
export class LogsPage {
  logContent: string | null = null;
  loading = false;
  error: string | null = null;

  constructor(private logService: LogService) {}

  viewLog() {
    this.loading = true;
    this.error = null;
    this.logService.getPipelineLog().subscribe({
      next: (data) => {
        this.logContent = data;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load log file';
        this.loading = false;
      }
    });
  }
}