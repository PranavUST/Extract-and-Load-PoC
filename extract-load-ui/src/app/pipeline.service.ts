import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class PipelineService {
  private apiUrl = 'http://127.0.0.1:5000';

  constructor(private http: HttpClient) {}

  runPipeline(configFile: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/run-pipeline`, { config_file: configFile });
  }

  getStatus(): Observable<any> {
    return this.http.get(`${this.apiUrl}/pipeline-status`);
  }
}