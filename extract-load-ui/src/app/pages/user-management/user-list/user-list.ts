import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { UserManagementService, User } from '../../../services/user-management.service';
import { AuthService } from '../../../services/auth.service';

@Component({
  standalone: true,
  selector: 'app-user-list',
  templateUrl: './user-list.html',
  styleUrls: ['./user-list.scss'],
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatSelectModule,
    MatProgressSpinnerModule
  ]
})
export class UserList implements OnInit {
  displayedColumns = ['name', 'username', 'email', 'role', 'lastLogin', 'actions'];
  users: User[] = [];
  loading = false;
  currentUsername: string | null = null;

  constructor(
    private userManagementService: UserManagementService,
    private authService: AuthService
  ) {}

  ngOnInit() {
    this.loadUsers();
    // Get current user to prevent self-deletion
    const currentUser = this.authService.getCurrentUser();
    if (currentUser) {
      this.currentUsername = currentUser.username;
    }
  }

  loadUsers() {
    this.loading = true;
    this.userManagementService.getUsers().subscribe({
      next: (response) => {
        if (response.success) {
          this.users = response.users;
        }
        this.loading = false;
      },
      error: (err) => {
        console.error('Failed to load users:', err);
        this.loading = false;
      }
    });
  }

  updateUserRole(user: User) {
    this.userManagementService.updateUserRole(user.id, user.role).subscribe({
      next: (response) => {
        if (response.success) {
          console.log('User role updated successfully');
        }
      },
      error: (err) => {
        console.error('Failed to update user role:', err);
        this.loadUsers(); // Reload to reset the UI
      }
    });
  }

  deleteUser(user: User) {
    if (confirm(`Are you sure you want to delete user "${user.name}"?`)) {
      this.userManagementService.deleteUser(user.id).subscribe({
        next: (response) => {
          if (response.success) {
            this.loadUsers(); // Refresh the list
          }
        },
        error: (err) => {
          console.error('Failed to delete user:', err);
        }
      });
    }
  }

  isCurrentUser(user: User): boolean {
    return user.username === this.currentUsername;
  }
}
