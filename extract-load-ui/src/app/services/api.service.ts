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
  runPipelineOnce(config: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/run-pipeline-once`, config);
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
  getCurrentConfig(): Observable<any> {
    return this.http.get(`${this.apiUrl}/current-config`);
  }
  getSourceConfigs(): Observable<any[]> {
    // Use the correct endpoint for GET
    return this.http.get<any[]>(`${this.apiUrl}/saved-source-configs`);
  }
  getLatestScheduledRunId(): Observable<{run_id: string}> {
    return this.http.get<{run_id: string}>(`${this.apiUrl}/latest-scheduled-run-id`);
  }
  getPipelineStatusByRunId(runId: string): Observable<{status: {timestamp: string, message: string}[]}> {
    return this.http.get<{status: {timestamp: string, message: string}[]}>(`${this.apiUrl}/pipeline-status?run_id=${runId}`);
  }

  get apiBaseUrl(): string {
    return this.apiUrl;
  }
}
