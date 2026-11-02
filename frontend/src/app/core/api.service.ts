import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { API_URL } from './auth.service';
import { AdminStats, GeneratedFile, Pipeline, Project, Run, RunLogs, User } from './models';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);
  projects() { return this.http.get<Project[]>(`${API_URL}/projects`); }
  createProject(payload: { name: string; description?: string }) { return this.http.post<Project>(`${API_URL}/projects`, payload); }
  deleteProject(id: number) { return this.http.delete<void>(`${API_URL}/projects/${id}`); }
  pipelines() { return this.http.get<Pipeline[]>(`${API_URL}/pipelines`); }
  createPipeline(payload: object) { return this.http.post<Pipeline>(`${API_URL}/pipelines`, payload); }
  deletePipeline(id: number) { return this.http.delete<void>(`${API_URL}/pipelines/${id}`); }
  runs() { return this.http.get<Run[]>(`${API_URL}/runs`); }
  createRun(payload: { pipeline_id: number; max_retries?: number; timeout_seconds?: number }) {
    return this.http.post<Run>(`${API_URL}/runs`, payload);
  }
  executeRun(id: number) { return this.http.post<Run>(`${API_URL}/runs/${id}/execute`, {}); }
  cancelRun(id: number) { return this.http.post<Run>(`${API_URL}/runs/${id}/cancel`, {}); }
  logs(id: number) { return this.http.get<RunLogs>(`${API_URL}/runs/${id}/logs`); }
  files() { return this.http.get<GeneratedFile[]>(`${API_URL}/generated-files`); }
  createFile(payload: object) { return this.http.post<GeneratedFile>(`${API_URL}/generated-files`, payload); }
  updateFile(id: number, payload: { file_type?: string; path?: string; content?: string; version?: number; is_user_edited?: boolean }) {
    return this.http.put<GeneratedFile>(`${API_URL}/generated-files/${id}`, payload);
  }
  deleteFile(id: number) { return this.http.delete<void>(`${API_URL}/generated-files/${id}`); }
  updateUser(id: number, payload: { username?: string; email?: string; password?: string }) {
    return this.http.put<User>(`${API_URL}/users/${id}`, payload);
  }
  users() { return this.http.get<User[]>(`${API_URL}/users`); }
  changeRole(id: number, role: string) {
    return this.http.put<User>(`${API_URL}/auth/${id}/role`, { role });
  }
  adminStats() { return this.http.get<AdminStats>(`${API_URL}/admin/stats`); }
}
