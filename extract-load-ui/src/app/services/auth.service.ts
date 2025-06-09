import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable, tap } from 'rxjs';

export interface User {
  name: string;
  email: string;
  username: string;
  role: 'Admin' | 'User';
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private apiUrl = 'http://localhost:5000/api'; // Update if your Flask API uses different URL
  private currentUserSubject = new BehaviorSubject<User | null>(this.getStoredUser());
  
  constructor(private http: HttpClient, private router: Router) {}

  // Login with backend API
  login(username: string, password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/login`, { username, password }).pipe(
      tap((response: any) => {
        if (response.success) {
          const user = {
            username: response.username,
            role: response.role,
            name: '', // These will be populated after full profile fetch
            email: ''
          };
          sessionStorage.setItem('authData', JSON.stringify(user));
          this.currentUserSubject.next(user);
        }
      })
    );
  }

  // Register with backend API
  register(userData: {
    name: string,
    email: string,
    username: string,
    password: string,
    role: 'User' | 'Admin'
  }): Observable<any> {
    return this.http.post(`${this.apiUrl}/register`, userData);
  }

  // Logout and clear session
  logout(): void {
    sessionStorage.removeItem('authData');
    this.currentUserSubject.next(null);
    this.router.navigate(['/login']);
  }

  // Get current user observable
  get currentUser$(): Observable<User | null> {
    return this.currentUserSubject.asObservable();
  }

  // Check if user is logged in
  isLoggedIn(): boolean {
    return !!this.currentUserSubject.value;
  }

  // Get user role
  getUserRole(): 'Admin' | 'User' | null {
    return this.currentUserSubject.value?.role || null;
  }

  // Get stored user from session storage
  private getStoredUser(): User | null {
    const authData = sessionStorage.getItem('authData');
    return authData ? JSON.parse(authData) : null;
  }
}
