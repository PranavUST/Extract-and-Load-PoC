import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { ApiService } from '../../../services/api.service';
import { MatCardModule } from '@angular/material/card';


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

  sourceTypes = ['API', 'FTP'];
  sourceForm: FormGroup = this.fb.group({
    name: ['', Validators.required],
    type: ['API', Validators.required],
    endpoint: [''],
    authToken: [''],
    ftpHost: ['']
  });

  saveConfig() {
    if (this.sourceForm.valid) {
      this.api.saveSourceConfig(this.sourceForm.value).subscribe({
        next: (res) => alert('Source config saved!'),
        error: (err) => alert('Save failed: ' + err.message)
      });
    }
  }
}
