import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private apiUrl = 'http://localhost:5000';

  constructor(private http: HttpClient) {}

  runPipeline(config: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/run-pipeline`, config);
  }
  getPipelineStatus(): Observable<any> {
    return this.http.get(`${this.apiUrl}/pipeline-status`);
  }
  stopPipeline(): Observable<any> {
    return this.http.post(`${this.apiUrl}/stop-pipeline`, {});
  }
  saveSourceConfig(config: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/source-configs`, config);
  }
  saveTargetConfig(config: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/target-configs`, config);
  }
  getUsers(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/v1/data`);
  }
  updateUser(user: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/users/${user.id}`, user);
  }
  deleteUser(userId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/users/${userId}`);
  }
}
