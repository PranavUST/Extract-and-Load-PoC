import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatOptionModule } from '@angular/material/core';
import { MatChipsModule } from '@angular/material/chips';

@Component({
  standalone: true,
  selector: 'app-scheduler-config',
  templateUrl: './scheduler-config.component.html',
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatOptionModule,
    MatButtonModule,
    MatChipsModule
  ]
})
export class SchedulerConfigComponent {
  schedulerForm: FormGroup;
  pipelines = [
    { id: 1, name: 'Daily Sales Report' },
    { id: 2, name: 'Inventory Sync' }
  ];

  constructor(private fb: FormBuilder) {
    this.schedulerForm = this.fb.group({
      cronExpression: ['*/5 * * * *', Validators.required],
      pipeline: ['', Validators.required]
    });
  }

  saveSchedule() {
    if (this.schedulerForm.valid) {
      console.log('Schedule:', this.schedulerForm.value);
    }
  }
}
