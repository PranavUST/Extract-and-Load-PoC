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
  selector: 'app-target-config',
  templateUrl: './target-config.html',
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
export class TargetConfig {
  private fb = inject(FormBuilder);
  private api = inject(ApiService);
  targetTypes = ['Database'];

  targetForm = this.fb.group({
    name: ['', Validators.required],
    type: ['Database', Validators.required],
    tableName: ['', Validators.required],
    //connectionString: ['', Validators.required],
  });

  saveConfig() {
    if (this.targetForm.valid) {
      this.api.saveTargetConfig(this.targetForm.value).subscribe({
        next: (res) => alert('Target config saved!'),
        error: (err) => alert('Save failed: ' + err.message)
      });
    }
  }
}
