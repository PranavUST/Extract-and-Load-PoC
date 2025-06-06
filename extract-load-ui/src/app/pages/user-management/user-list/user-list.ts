import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { MatChipsModule } from '@angular/material/chips';
import { ApiService } from '../../../services/api.service';

interface User {
  id: number;
  name: string;
  role: string;
  permissions: string[];
}

@Component({
  standalone: true,
  selector: 'app-user-list',
  templateUrl: './user-list.html',
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatSelectModule,
    MatChipsModule
  ]
})
export class UserList implements OnInit {
  private api = inject(ApiService);

  displayedColumns = ['name', 'role', 'permissions', 'actions'];
  roles = ['admin', 'operator', 'viewer'];
  users: User[] = [];

  ngOnInit() {
    this.loadUsers();
  }

  loadUsers() {
    this.api.getUsers().subscribe(users => this.users = users);
  }

  updateUser(user: User) {
    this.api.updateUser(user).subscribe(() => this.loadUsers());
  }

  deleteUser(user: User) {
    this.api.deleteUser(user.id).subscribe(() => this.loadUsers());
  }
}
