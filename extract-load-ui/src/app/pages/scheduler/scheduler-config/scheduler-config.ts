import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { ApiService } from '../../../services/api.service';

@Component({
  standalone: true,
  selector: 'app-scheduler-config',
  templateUrl: './scheduler-config.html',
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatCardModule
  ]
})
export class SchedulerConfig {
  private fb = inject(FormBuilder);
  private api = inject(ApiService);

  status = '';
  schedulerForm: FormGroup = this.fb.group({
    configFile: ['', Validators.required]
  });

  runPipeline() {
    if (this.schedulerForm.valid) {
      // IMPORTANT: Send as { config_file: ... }
      const configFile = this.schedulerForm.value.configFile;
      this.api.runPipeline({ config_file: configFile }).subscribe({
        next: () => this.status = 'Pipeline started successfully',
        error: (err) => this.status = `Error: ${err.message}`
      });
    }
  }
}
