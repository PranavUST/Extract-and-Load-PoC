import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';

@Component({
  standalone: true,
  selector: 'app-source-config',
  templateUrl: './source-config.component.html',
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatChipsModule
  ]
})
export class SourceConfigComponent {
  sourceForm: FormGroup;
  sourceTypes = ['REST API', 'FTP', 'Database'];

  constructor(private fb: FormBuilder) {
    this.sourceForm = this.fb.group({
      sourceType: ['REST API', Validators.required],
      apiUrl: ['', Validators.required],
      authToken: [''],
      ftpHost: [''],
      ftpUser: ['']
    });
  }

  saveConfig() {
    if (this.sourceForm.valid) {
      console.log('Source Config:', this.sourceForm.value);
    }
  }
}
