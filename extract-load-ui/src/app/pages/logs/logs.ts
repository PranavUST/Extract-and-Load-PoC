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
        // Reverse the log lines so latest logs appear first
        const lines = data.split(/\r?\n/).filter(line => line.trim().length > 0);
        this.logContent = lines.reverse().join('\n');
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load log file';
        this.loading = false;
      }
    });
  }

  async downloadLog() {
    const url = 'http://localhost:5000/api/pipeline-log';
    try {
      const response = await fetch(url, { credentials: 'include' });
      if (!response.ok) throw new Error('Network response was not ok');
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = 'pipeline.log';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (err) {
      alert('Failed to download log file.');
    }
  }
}