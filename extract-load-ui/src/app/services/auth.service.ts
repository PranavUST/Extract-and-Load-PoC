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
  private apiUrl = 'http://localhost:5000/api';
  private currentUserSubject = new BehaviorSubject<User | null>(this.getStoredUser());

  constructor(private http: HttpClient, private router: Router) {}

  // Login with backend API
  login(username: string, password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/login`, { username, password }, { 
      withCredentials: true 
    }).pipe(
      tap((response: any) => {
        if (response.success) {
          const user = {
            name: response.name || '',
            email: response.email || '',
            username: response.username,
            role: response.role
          };
          sessionStorage.setItem('currentUser', JSON.stringify(user));
          this.currentUserSubject.next(user);
        }
      })
    );
  }

  // Login with backend API, with rememberMe support
  loginWithRemember(username: string, password: string, rememberMe: boolean): Observable<any> {
    return this.http.post(`${this.apiUrl}/login`, { username, password }, { 
      withCredentials: true 
    }).pipe(
      tap((response: any) => {
        if (response.success) {
          const user = {
            name: response.name || '',
            email: response.email || '',
            username: response.username,
            role: response.role
          };
          if (rememberMe) {
            localStorage.setItem('currentUser', JSON.stringify(user));
            sessionStorage.removeItem('currentUser');
          } else {
            sessionStorage.setItem('currentUser', JSON.stringify(user));
            localStorage.removeItem('currentUser');
          }
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
    this.http.post(`${this.apiUrl}/logout`, {}, { withCredentials: true }).subscribe(() => {
      sessionStorage.removeItem('currentUser');
      localStorage.removeItem('currentUser');
      this.currentUserSubject.next(null);
      this.router.navigate(['/login']);
      this.clearCookies();
    });
  }

  // Get current user observable
  get currentUser$(): Observable<User | null> {
    return this.currentUserSubject.asObservable();
  }

  // Check if user is logged in
  isLoggedIn(): boolean {
    return !!this.currentUserSubject.value;
  }

  // Get current user info
  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }

  // Get user role
  getUserRole(): 'Admin' | 'User' | null {
    return this.currentUserSubject.value?.role || null;
  }

  /**
   * Ensures currentUserSubject is set from storage if not already set.
   * Call this before checking isLoggedIn() in guards.
   */
  rehydrateUserFromStorage(): void {
    if (!this.currentUserSubject.value) {
      const userData = localStorage.getItem('currentUser') || sessionStorage.getItem('currentUser');
      if (userData) {
        this.currentUserSubject.next(JSON.parse(userData));
      }
    }
  }

  private clearCookies() {
    document.cookie = 'session=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
  }

  private getStoredUser(): User | null {
    const userData = localStorage.getItem('currentUser') || sessionStorage.getItem('currentUser');
    return userData ? JSON.parse(userData) : null;
  }
}
