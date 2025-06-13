import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatIconModule,
    RouterLink
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

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit() {}

  onSubmit(): void {
    if (this.username && this.password) {
      
      this.authService.login(this.username, this.password).subscribe({
        next: (response) => {
          if (response.success) {
            this.router.navigate(['/landing']);
          } else {
            this.loginError = true;
            this.errorMessage = 'Invalid Username or Password';
          }
        },
        error: () => {
          this.loginError = true;
          this.errorMessage = 'Invalid Username or Password';
        }
      });
    }
  }

  togglePasswordVisibility() {
    this.hidePassword = !this.hidePassword;
  }
}
