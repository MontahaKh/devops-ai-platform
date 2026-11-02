import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../core/auth.service';

@Component({
  selector: 'app-login',
  imports: [CommonModule, FormsModule, RouterLink],
  template: `<main class="login"><form (ngSubmit)="submit()"><div class="brand"><b>D</b><span>DevOps AI Platform</span></div><h1>Welcome back</h1><p>Sign in to manage your infrastructure.</p><label>Username<input name="username" [(ngModel)]="username" required minlength="3" maxlength="50" autocomplete="username"></label><label>Password<input name="password" [(ngModel)]="password" required minlength="8" type="password" autocomplete="current-password"></label><button [disabled]="loading">{{ loading ? 'Signing in…' : 'Sign in' }}</button><div class="error" *ngIf="error">{{ error }}</div><small>Need an account? <a routerLink="/register">Register here</a></small></form></main>`,
  styles: [`.login{min-height:100vh;display:grid;place-items:center;background:#12131c;color:#fff}.login form{width:min(390px,calc(100% - 32px));background:#1d1e2a;border:1px solid #303140;border-radius:14px;padding:32px}.brand{display:flex;align-items:center;gap:10px;color:#d9d7ff}.brand b{display:grid;place-items:center;background:#7068f4;width:34px;height:34px;border-radius:9px}.login h1{margin:34px 0 8px}.login p,.login small{color:#999aaa;font-size:12px}.login label{display:block;color:#c9c9d4;font-size:12px;margin-top:20px}.login input{display:block;width:100%;box-sizing:border-box;margin-top:7px;padding:12px;border-radius:7px;border:1px solid #3b3c4c;background:#141520;color:#fff}.login button{margin-top:25px;width:100%;padding:12px;border:0;border-radius:7px;background:#7068f4;color:white;font-weight:600;cursor:pointer}.login button:disabled{opacity:.6}.error{color:#ff929b;background:#3a2229;padding:10px;border-radius:6px;margin-top:14px;font-size:12px}.login a{color:#b7b2ff}`],
})
export class LoginComponent {
  private readonly auth = inject(AuthService); private readonly router = inject(Router);
  username = ''; password = ''; loading = false; error = '';
  submit() {
    this.loading = true;
    this.error = '';
    this.auth.login(this.username, this.password).subscribe({
      next: () => this.router.navigate(['/dashboard']),
      error: err => {
        this.error = this.formatError(err);
        this.loading = false;
      },
      complete: () => this.loading = false,
    });
  }
  private formatError(err: { status?: number; error?: { detail?: string | { msg?: string }[] } }) {
    const detail = err.error?.detail;
    if (Array.isArray(detail)) return detail.map(item => item.msg || 'Invalid value').join(' ');
    if (typeof detail === 'string') return detail;
    return err.status === 422 ? 'Username and password are required; the password must contain at least 8 characters.' : 'Unable to sign in.';
  }
}
