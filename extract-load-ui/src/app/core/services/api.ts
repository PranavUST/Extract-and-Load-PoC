import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private apiUrl = 'http://localhost:5000/api'; // Your Python API URL

  constructor(private http: HttpClient) { }

  // Example methods
  getConfigurations(): Observable<any> {
    return this.http.get(`${this.apiUrl}/configs`);
  }

  saveSchedule(schedule: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/schedules`, schedule);
  }

  getUsers(): Observable<any> {
    return this.http.get(`${this.apiUrl}/users`);
  }
}
