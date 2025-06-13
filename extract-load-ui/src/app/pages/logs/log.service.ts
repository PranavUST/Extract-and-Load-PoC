import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class LogService {
  constructor(private http: HttpClient) {}

  getPipelineLog(): Observable<string> {
    // Use the full backend URL
    return this.http.get('http://localhost:5000/api/pipeline-log', { responseType: 'text', withCredentials: true });
  }
}