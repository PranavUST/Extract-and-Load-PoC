import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';

@Component({
  standalone: true,
  selector: 'app-landing',
  templateUrl: './landing.html',
  styleUrls: ['./landing.scss'],
  imports: [CommonModule, RouterModule, MatButtonModule]
})
export class Landing {}
