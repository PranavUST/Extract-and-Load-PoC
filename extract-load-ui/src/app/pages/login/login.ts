import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatIconModule,
    RouterLink,
    MatProgressSpinnerModule
  ],
  templateUrl: './login.html',
  styleUrls: ['./login.scss']
})
export class LoginComponent implements OnInit {
  username = '';
  password = '';
  errorMessage = '';
  loginError = false;
  hidePassword = true;
  loading = false;
  rememberMe = false;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit() {
    // If already logged in, redirect to landing
    this.authService.rehydrateUserFromStorage();
    if (this.authService.isLoggedIn()) {
      this.router.navigate(['/landing']);
      return;
    }
    // Autofill username if user is in localStorage (Remember Me)
    const userData = localStorage.getItem('currentUser');
    if (userData) {
      try {
        const user = JSON.parse(userData);
        if (user && user.username) {
          this.username = user.username;
          this.rememberMe = true;
        }
      } catch {}
    }
  }

  onSubmit(): void {
    if (this.username && this.password) {
      this.loading = true;
      this.authService.loginWithRemember(this.username, this.password, this.rememberMe).subscribe({
        next: (response) => {
          this.loading = false;
          if (response.success) {
            this.router.navigate(['/landing']);
          } else {
            this.loginError = true;
            this.errorMessage = 'Invalid Username or Password';
            setTimeout(() => this.errorMessage = '', 600); // clear error for shake
          }
        },
        error: () => {
          this.loading = false;
          this.loginError = true;
          this.errorMessage = 'Invalid Username or Password';
          setTimeout(() => this.errorMessage = '', 600); // clear error for shake
        }
      });
    }
  }

  togglePasswordVisibility() {
    this.hidePassword = !this.hidePassword;
  }
}
