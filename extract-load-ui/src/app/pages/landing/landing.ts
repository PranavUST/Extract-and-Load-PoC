import { Component } from '@angular/core';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';  // <-- Import MatCardModule here

@Component({
  selector: 'app-landing',
  standalone: true,
  templateUrl: './landing.html',
  styleUrls: ['./landing.scss'],
  imports: [CommonModule, RouterLink, MatButtonModule, MatCardModule]
})
export class Landing {
  constructor(
    public authService: AuthService,
    private router: Router
  ) {}

  get currentUser() {
    return this.authService.getCurrentUser();
  }

  get userRole() {
    return this.authService.getUserRole();
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}

