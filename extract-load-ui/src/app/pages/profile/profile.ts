import { Component, OnInit } from '@angular/core';
import { AuthService } from '../../services/auth.service';
import { ApiService } from '../../core/services/api';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-profile',
  templateUrl: './profile.html',
  styleUrls: ['./profile.scss'],
  imports: [CommonModule, MatIconModule, RouterLink]
})
export class ProfileComponent implements OnInit {
  user: any;
  loading = true;
  error = '';

  constructor(private authService: AuthService, private api: ApiService) {}

  ngOnInit() {
    const currentUser = this.authService.getCurrentUser();
    if (currentUser && currentUser.username) {
      this.api.getUsers().subscribe({
        next: (res: any) => {
          // Find the user in the users list by username
          if (Array.isArray(res.users)) {
            this.user = res.users.find((u: any) => u.username === currentUser.username);
          } else if (Array.isArray(res)) {
            this.user = res.find((u: any) => u.username === currentUser.username);
          }
          this.loading = false;
        },
        error: (err) => {
          this.error = 'Failed to load user details.';
          this.loading = false;
        }
      });
    } else {
      this.loading = false;
      this.error = 'No user logged in.';
    }
  }
}
