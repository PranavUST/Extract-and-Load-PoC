import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-login',
  standalone: true,
  templateUrl: './login.html',
  styleUrls: ['./login.scss'],
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    RouterLink
  ]
})
export class Login {
  loginForm: FormGroup;
  errorMessage = '';
  loginError = false;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      username: ['', Validators.required],
      password: ['', Validators.required]
    });
  }

  onSubmit(): void {
  if (this.loginForm.valid) {
    const { username, password } = this.loginForm.value;
    
    this.authService.login(username, password).subscribe({
      next: (response) => {
        if (response.success) {
          this.router.navigate(['/landing']);
        } else {
          this.loginError = true;
          this.errorMessage = 'Invalid credentials';
        }
      },
      error: (err) => {
        this.loginError = true;
        this.errorMessage = err.error?.error || 'Login failed. Please try again.';
      }
    });
  }
}


}
