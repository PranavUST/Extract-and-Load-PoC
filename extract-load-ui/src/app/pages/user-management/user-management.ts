import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UserList } from './user-list/user-list';

@Component({
  standalone: true,
  selector: 'app-user-management',
  templateUrl: './user-management.html',
  styleUrls: ['./user-management.scss'],
  imports: [CommonModule, UserList]
})
export class UserManagement {}
