import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { ApiService } from '../../../services/api.service';
import { MatCardModule } from '@angular/material/card';
import { Output, EventEmitter } from '@angular/core';


@Component({
  standalone: true,
  selector: 'app-source-config',
  templateUrl: './source-config.html',
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatCardModule
  ]
})
export class SourceConfig {
  private fb = inject(FormBuilder);
  private api = inject(ApiService);
  @Output() configSaved = new EventEmitter<void>();
  sourceTypes = ['API', 'FTP'];
  public sourceForm: FormGroup = this.fb.group({
    name: ['', Validators.required],
    type: ['API', Validators.required],
    endpoint: ['', Validators.required], // Ensure required for API
    authToken: [''],
    ftpHost: ['', Validators.required], // Ensure required for FTP
    ftpUsername: [''],
    ftpPassword: [''],
    retries: [3] 
  });
  constructor() {
    this.sourceForm.get('type')?.valueChanges.subscribe(type => {
      if (type === 'API') {
        this.sourceForm.get('endpoint')?.setValidators([Validators.required]);
        this.sourceForm.get('ftpHost')?.clearValidators();
        this.sourceForm.get('ftpUsername')?.clearValidators();
        this.sourceForm.get('ftpPassword')?.clearValidators();
      } else if (type === 'FTP') {
        this.sourceForm.get('ftpHost')?.setValidators([Validators.required]);
        this.sourceForm.get('endpoint')?.clearValidators();
        this.sourceForm.get('authToken')?.clearValidators();
      }
      this.sourceForm.get('endpoint')?.updateValueAndValidity();
      this.sourceForm.get('ftpHost')?.updateValueAndValidity();
      this.sourceForm.get('ftpUsername')?.updateValueAndValidity();
      this.sourceForm.get('ftpPassword')?.updateValueAndValidity();
      this.sourceForm.get('authToken')?.updateValueAndValidity();
    });
  }
  saveConfig() {
    if (this.sourceForm.valid) {
      this.api.saveSourceConfig(this.sourceForm.value).subscribe({
        next: (res) => {
          alert('Source config saved!'),
          this.configSaved.emit();
        },
        error: (err) => alert('Save failed: ' + err.message)
      });
    } 
  }
}