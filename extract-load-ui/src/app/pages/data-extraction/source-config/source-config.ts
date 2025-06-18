import { Component, inject, Input } from '@angular/core';
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
  @Input() advancedSettings: any; // Accept advanced settings from parent
  sourceTypes = ['API', 'FTP'];
  public sourceForm: FormGroup = this.fb.group({
    name: ['', [Validators.required, this.trimValidator]],
    type: ['', Validators.required],
    endpoint: ['', [Validators.required, this.trimValidator]], // Ensure required for API
    authToken: [''],
    ftpHost: ['', [Validators.required, this.trimValidator]], // Ensure required for FTP
    ftpUsername: [''],
    ftpPassword: [''],
    retries: [3] 
  });

  trimValidator(control: import('@angular/forms').AbstractControl) {
    if (typeof control.value === 'string' && control.value.trim().length === 0) {
      return { required: true };
    }
    return null;
  }

  constructor() {
    this.sourceForm.get('type')?.valueChanges.subscribe(type => {
      if (type === 'API') {
        this.sourceForm.get('endpoint')?.setValidators([Validators.required, this.trimValidator]);
        this.sourceForm.get('ftpHost')?.clearValidators();
        this.sourceForm.get('ftpUsername')?.clearValidators();
        this.sourceForm.get('ftpPassword')?.clearValidators();
      } else if (type === 'FTP') {
        this.sourceForm.get('ftpHost')?.setValidators([Validators.required, this.trimValidator]);
        this.sourceForm.get('endpoint')?.clearValidators();
        this.sourceForm.get('authToken')?.clearValidators();
      }
      // Always trim the value for endpoint and ftpHost
      const endpoint = this.sourceForm.get('endpoint')?.value;
      if (typeof endpoint === 'string') {
        this.sourceForm.get('endpoint')?.setValue(endpoint.trim(), { emitEvent: false });
      }
      const ftpHost = this.sourceForm.get('ftpHost')?.value;
      if (typeof ftpHost === 'string') {
        this.sourceForm.get('ftpHost')?.setValue(ftpHost.trim(), { emitEvent: false });
      }
      this.sourceForm.get('endpoint')?.updateValueAndValidity();
      this.sourceForm.get('ftpHost')?.updateValueAndValidity();
      this.sourceForm.get('ftpUsername')?.updateValueAndValidity();
      this.sourceForm.get('ftpPassword')?.updateValueAndValidity();
      this.sourceForm.get('authToken')?.updateValueAndValidity();
    });

    // Fix: Also trim and update validity on blur for endpoint and ftpHost
    this.sourceForm.get('endpoint')?.valueChanges.subscribe(val => {
      if (typeof val === 'string' && val !== val.trim()) {
        this.sourceForm.get('endpoint')?.setValue(val.trim(), { emitEvent: false });
        this.sourceForm.get('endpoint')?.updateValueAndValidity();
      }
    });
    this.sourceForm.get('ftpHost')?.valueChanges.subscribe(val => {
      if (typeof val === 'string' && val !== val.trim()) {
        this.sourceForm.get('ftpHost')?.setValue(val.trim(), { emitEvent: false });
        this.sourceForm.get('ftpHost')?.updateValueAndValidity();
      }
    });
  }

  onEndpointBlur() {
    const ctrl = this.sourceForm.get('endpoint');
    if (ctrl && typeof ctrl.value === 'string') {
      ctrl.setValue(ctrl.value.trim());
      ctrl.updateValueAndValidity();
    }
  }

  onFtpHostBlur() {
    const ctrl = this.sourceForm.get('ftpHost');
    if (ctrl && typeof ctrl.value === 'string') {
      ctrl.setValue(ctrl.value.trim());
      ctrl.updateValueAndValidity();
    }
  }

  onEndpointInput() {
    const ctrl = this.sourceForm.get('endpoint');
    if (ctrl && typeof ctrl.value === 'string') {
      const trimmed = ctrl.value.trim();
      if (ctrl.value !== trimmed) {
        ctrl.setValue(trimmed); // emitEvent defaults to true
      }
      ctrl.updateValueAndValidity();
    }
  }

  onFtpHostInput() {
    const ctrl = this.sourceForm.get('ftpHost');
    if (ctrl && typeof ctrl.value === 'string') {
      const trimmed = ctrl.value.trim();
      if (ctrl.value !== trimmed) {
        ctrl.setValue(trimmed); // emitEvent defaults to true
      }
      ctrl.updateValueAndValidity();
    }
  }

  saveConfig() {
    if (this.sourceForm.valid) {
      // Merge advanced settings with source config
      const payload = {
        ...this.sourceForm.value,
        advanced: this.advancedSettings ? this.advancedSettings.value : {}
      };
      this.api.saveSourceConfig(payload).subscribe({
        next: (res) => {
          alert('Source config saved!'),
          this.configSaved.emit();
        },
        error: (err) => alert('Save failed: ' + err.message)
      });
    } 
  }
}