import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

export interface TargetConfig {
  name: string;
  tableName?: string;
  type?: string;
}

@Component({
  selector: 'app-edit-target-config-dialog',
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
    <h2 mat-dialog-title>Edit Target Config</h2>
    <mat-dialog-content>
      <form #editForm="ngForm">
        <mat-form-field>
          <input matInput placeholder="Name" [(ngModel)]="data.name" name="name" required>
        </mat-form-field>
        <mat-form-field>
          <mat-label>Target Type</mat-label>
          <mat-select [(ngModel)]="data.type" name="type" required>
            <mat-option value="Database">Database</mat-option>
            <!-- Add more target types if needed -->
          </mat-select>
        </mat-form-field>
        <ng-container *ngIf="data.type === 'Database'">
          <mat-form-field>
            <input matInput placeholder="Table Name" [(ngModel)]="data.tableName" name="tableName" required>
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
export class EditTargetConfigDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<EditTargetConfigDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: TargetConfig
  ) {}

  onCancel(): void {
    this.dialogRef.close();
  }

  onSave(): void {
    this.dialogRef.close(this.data);
  }
}