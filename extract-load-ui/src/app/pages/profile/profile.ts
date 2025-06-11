import { Component, OnInit } from '@angular/core';
import { AuthService } from '../../services/auth.service';
import { ApiService } from '../../core/services/api';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { RouterLink } from '@angular/router';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-profile',
  templateUrl: './profile.html',
  styleUrls: ['./profile.scss'],
  imports: [CommonModule, MatIconModule, RouterLink, FormsModule, ReactiveFormsModule]
})
export class ProfileComponent implements OnInit {
  user: any;
  loading = true;
  error = '';
  saving = false;
  saveSuccess = false;
  saveError = '';
  editing = false;
  profileForm: FormGroup;
  passwordForm: FormGroup;
  passwordChangeSuccess = false;
  passwordChangeError = '';
  showPasswordForm = false;
  showNewPassword = false;
  showConfirmPassword = false;

  constructor(private authService: AuthService, private api: ApiService, private fb: FormBuilder) {
    this.profileForm = this.fb.group({
      name: ['', [Validators.required, Validators.pattern(/^[A-Za-z ]{2,}$/)]],
      email: ['', [Validators.required, Validators.email]],
      username: ['', [Validators.required, Validators.minLength(3), Validators.pattern(/^[A-Za-z0-9_]+$/)]]
    });
    this.passwordForm = this.fb.group({
      newPassword: ['', [Validators.required, Validators.minLength(6), Validators.pattern(/^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]{6,}$/)]],
      confirmPassword: ['', [Validators.required]]
    }, { validators: this.passwordsMatchValidator });
  }

  ngOnInit() {
    this.api.getProfile().subscribe({
      next: (res: any) => {
        if (res && res.success && res.user) {
          this.user = res.user;
          this.profileForm.patchValue({
            name: this.user.name,
            email: this.user.email,
            username: this.user.username
          });
        } else {
          this.error = res?.error || 'Failed to load user details.';
        }
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load user details.';
        this.loading = false;
      }
    });
  }

  startEdit() {
    this.editing = true;
    this.saveSuccess = false;
    this.saveError = '';
    this.profileForm.patchValue({
      name: this.user.name,
      email: this.user.email,
      username: this.user.username
    });
  }

  cancelEdit() {
    this.editing = false;
    this.saveSuccess = false;
    this.saveError = '';
    this.profileForm.patchValue({
      name: this.user.name,
      email: this.user.email,
      username: this.user.username
    });
  }

  saveProfile() {
    if (!this.user || !this.user.id || this.profileForm.invalid) {
      this.profileForm.markAllAsTouched();
      return;
    }
    this.saving = true;
    this.saveSuccess = false;
    this.saveError = '';
    const { name, email, username } = this.profileForm.value;
    this.api.updateUser(this.user.id, { name, email, username }).subscribe({
      next: (res: any) => {
        this.saving = false;
        if (res.success) {
          this.saveSuccess = true;
          this.editing = false;
          this.user = { ...this.user, name, email, username };
        } else {
          this.saveError = res.error || 'Save failed.';
        }
      },
      error: (err) => {
        this.saving = false;
        this.saveError = err.error?.error || 'Save failed.';
      }
    });
  }

  passwordsMatchValidator(form: FormGroup) {
    return form.get('newPassword')?.value === form.get('confirmPassword')?.value ? null : { mismatch: true };
  }

  changePassword() {
    this.passwordChangeSuccess = false;
    this.passwordChangeError = '';
    if (this.passwordForm.invalid) {
      this.passwordForm.markAllAsTouched();
      return;
    }
    const { newPassword, confirmPassword } = this.passwordForm.value;
    if (newPassword !== confirmPassword) {
      this.passwordChangeError = 'Passwords do not match.';
      return;
    }
    this.api.changePassword(this.user.id, newPassword).subscribe({
      next: (res: any) => {
        if (res.success) {
          this.passwordChangeSuccess = true;
          setTimeout(() => {
            this.passwordForm.reset();
            this.showPasswordForm = false;
            this.passwordChangeSuccess = false;
          }, 1800);
        } else {
          this.passwordChangeError = res.error || 'Password change failed.';
        }
      },
      error: (err: any) => {
        this.passwordChangeError = err?.error?.error || 'Password change failed.';
      }
    });
  }

  togglePasswordForm() {
    this.showPasswordForm = !this.showPasswordForm;
    this.passwordChangeSuccess = false;
    this.passwordChangeError = '';
    this.passwordForm.reset();
  }
}
