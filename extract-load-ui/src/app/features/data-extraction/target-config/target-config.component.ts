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
  selector: 'app-target-config',
  templateUrl: './target-config.component.html',
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
export class TargetConfigComponent {
  targetForm: FormGroup;
  targetTypes = ['CSV', 'Database', 'API'];

  constructor(private fb: FormBuilder) {
    this.targetForm = this.fb.group({
      targetType: ['CSV', Validators.required],
      csvPath: ['', Validators.required],
      dbHost: [''],
      dbTable: ['']
    });
  }

  saveConfig() {
    if (this.targetForm.valid) {
      console.log('Target Config:', this.targetForm.value);
    }
  }
}
