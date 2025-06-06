import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { MatChipsModule } from '@angular/material/chips';

interface User {
  id: number;
  name: string;
  role: 'admin' | 'operator' | 'viewer';
  permissions: string[];
}

@Component({
  standalone: true,
  selector: 'app-user-list',
  templateUrl: './user-list.component.html',
  imports: [
    CommonModule,
    FormsModule, // For ngModel
    MatCardModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatSelectModule,
    MatChipsModule,
  ]
})
export class UserListComponent {
  displayedColumns: string[] = ['name', 'role', 'permissions', 'actions'];
  users: User[] = [
    { id: 1, name: 'Admin User', role: 'admin', permissions: ['all'] },
    { id: 2, name: 'Data Operator', role: 'operator', permissions: ['run_pipeline'] },
    { id: 3, name: 'Viewer', role: 'viewer', permissions: ['view'] }
  ];
  roles = ['admin', 'operator', 'viewer'];
  allPermissions = ['all', 'run_pipeline', 'view', 'edit', 'delete'];

  updateUser(user: User) {
    console.log('Updated user:', user);
  }

  deleteUser(user: User) {
    this.users = this.users.filter(u => u.id !== user.id);
  }
}
