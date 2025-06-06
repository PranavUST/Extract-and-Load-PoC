import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SchedulerConfig } from './scheduler-config/scheduler-config';

@Component({
  standalone: true,
  selector: 'app-scheduler',
  templateUrl: './scheduler.html',
  imports: [CommonModule, SchedulerConfig]
})
export class Scheduler {}
