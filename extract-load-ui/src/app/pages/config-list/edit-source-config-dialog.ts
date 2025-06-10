import { CommonModule } from '@angular/common';
import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { FormsModule } from '@angular/forms';
import { SourceConfig } from './config-list';

@Component({
  selector: 'app-edit-source-config-dialog',
  standalone: true,
  imports: [
    CommonModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSelectModule,
    FormsModule
  ],
  template: `
    <h2 mat-dialog-title>Edit Source Config</h2>
    <mat-dialog-content>
      <form #editForm="ngForm">
        <mat-form-field>
          <input matInput placeholder="Name" [(ngModel)]="data.name" name="name" required>
        </mat-form-field>
        <mat-form-field>
          <mat-label>Type</mat-label>
          <mat-select [(ngModel)]="data.type" name="type" required (selectionChange)="onTypeChange($event.value)">
            <mat-option value="api">API</mat-option>
            <mat-option value="ftp">FTP</mat-option>
          </mat-select>
        </mat-form-field>

        <!-- API fields -->
        <ng-container *ngIf="data.type === 'api'">
          <mat-form-field>
            <input matInput placeholder="Endpoint" [(ngModel)]="data.endpoint" name="endpoint" required>
          </mat-form-field>
          <mat-form-field>
            <input matInput placeholder="Auth Token" [(ngModel)]="data.authToken" name="authToken" required>
          </mat-form-field>
          <mat-form-field>
            <input matInput type="number" placeholder="Retries" [(ngModel)]="data.retries" name="retries">
          </mat-form-field>
        </ng-container>

        <!-- FTP fields -->
        <ng-container *ngIf="data.type === 'ftp'">
          <mat-form-field>
            <input matInput placeholder="Host" [(ngModel)]="data.ftpHost" name="ftpHost" required>
          </mat-form-field>
          <mat-form-field>
            <input matInput placeholder="Username" [(ngModel)]="data.ftpUsername" name="ftpUsername" required>
          </mat-form-field>
          <mat-form-field>
            <input matInput placeholder="Password" [(ngModel)]="data.ftpPassword" name="ftpPassword" type="password" required>
          </mat-form-field>
          <mat-form-field>
            <input matInput type="number" placeholder="Retries" [(ngModel)]="data.retries" name="retries">
          </mat-form-field>
        </ng-container>
      </form>
    </mat-dialog-content>
    <mat-dialog-actions>
      <button mat-button (click)="onCancel()">Cancel</button>
      <button mat-button color="primary" (click)="onSave()">Save</button>
    </mat-dialog-actions>
  `
})
export class EditSourceConfigDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<EditSourceConfigDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: SourceConfig
  ) {
    this.onTypeChange(this.data.type);
  }

  onCancel(): void {
    this.dialogRef.close();
  }

  onSave(): void {
    this.dialogRef.close(this.data);
  }
  onTypeChange(type: string) {
    if (type === 'api') {
      this.data.ftpHost = undefined;
      this.data.ftpUsername = undefined;
      this.data.ftpPassword = undefined;
    } else if (type === 'ftp') {
      this.data.endpoint = undefined;
      this.data.authToken = undefined;
    }
  }
}