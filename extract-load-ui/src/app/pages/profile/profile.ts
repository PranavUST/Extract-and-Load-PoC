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

  constructor(private authService: AuthService, private api: ApiService, private fb: FormBuilder) {
    this.profileForm = this.fb.group({
      name: ['', [Validators.required, Validators.pattern(/^[A-Za-z ]{2,}$/)]],
      email: ['', [Validators.required, Validators.email]],
      username: ['', [Validators.required, Validators.minLength(3), Validators.pattern(/^[A-Za-z0-9_]+$/)]]
    });
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
}
