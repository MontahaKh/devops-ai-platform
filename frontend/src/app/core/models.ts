export interface User { id: number; username: string; email: string; role: string; is_active: boolean; created_at?: string; updated_at?: string; }
export interface AdminStats { users: number; projects: number; successful_runs: number; failed_runs: number; }
export interface Project { id: number; name: string; description?: string; owner_id: number; created_at: string; updated_at: string; }
export interface Pipeline { id: number; name: string; description?: string; project_id: number; definition: any; status: string; created_at: string; updated_at: string; }
export interface Run { id: number; pipeline_id: number; status: string; error_summary?: string; started_at?: string; finished_at?: string; created_at: string; correlation_id: string; retry_count: number; max_retries: number; timeout_seconds: number; celery_task_id?: string; }
export interface GeneratedFile { id: number; run_id: number; file_type: string; path: string; content: string; version: number; is_user_edited: boolean; created_at: string; }
export interface Validation { id: number; run_id: number; command: string; stdout?: string; stderr?: string; exit_code?: number; message?: string; status?: string; created_at: string; }
export interface RunLogs { run_id: number; status: string; validations: Validation[]; }
export interface TokenResponse { access_token: string; refresh_token: string; token_type: string; }
