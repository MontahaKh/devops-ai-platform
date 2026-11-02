import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../core/auth.service';

@Component({
  selector: 'app-register',
  imports: [CommonModule, FormsModule, RouterLink],
  template: `<main class="register"><form (ngSubmit)="submit()"><div class="brand"><b>D</b><span>DevOps AI Platform</span></div><h1>Create account</h1><p>Create a standard user account to get started.</p><label>Username<input name="username" [(ngModel)]="username" required minlength="3" maxlength="50" autocomplete="username"></label><label>Email<input name="email" [(ngModel)]="email" required type="email" autocomplete="email"></label><label>Password<input name="password" [(ngModel)]="password" required type="password" minlength="8" autocomplete="new-password"></label><button [disabled]="loading">{{ loading ? 'Creating account…' : 'Create account' }}</button><div class="success" *ngIf="success">{{ success }}</div><div class="error" *ngIf="error">{{ error }}</div><small>Already have an account? <a routerLink="/login">Sign in</a></small></form></main>`,
  styles: [`.register{min-height:100vh;display:grid;place-items:center;background:#12131c;color:#fff}.register form{width:min(390px,calc(100% - 32px));background:#1d1e2a;border:1px solid #303140;border-radius:14px;padding:32px}.brand{display:flex;align-items:center;gap:10px;color:#d9d7ff}.brand b{display:grid;place-items:center;background:#7068f4;width:34px;height:34px;border-radius:9px}.register h1{margin:34px 0 8px}.register p,.register small{color:#999aaa;font-size:12px}.register label{display:block;color:#c9c9d4;font-size:12px;margin-top:20px}.register input{display:block;width:100%;box-sizing:border-box;margin-top:7px;padding:12px;border-radius:7px;border:1px solid #3b3c4c;background:#141520;color:#fff}.register button{margin-top:25px;width:100%;padding:12px;border:0;border-radius:7px;background:#7068f4;color:white;font-weight:600;cursor:pointer}.register button:disabled{opacity:.6}.error,.success{padding:10px;border-radius:6px;margin-top:14px;font-size:12px}.error{color:#ff929b;background:#3a2229}.success{color:#a7f3c0;background:#1d3a2a}.register a{color:#b7b2ff}`],
})
export class RegisterComponent {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  username = '';
  email = '';
  password = '';
  loading = false;
  error = '';
  success = '';

  submit() {
    this.loading = true;
    this.error = '';
    this.success = '';
    this.auth.register(this.username, this.email, this.password).subscribe({
      next: () => {
        this.success = 'Account created. You can now sign in.';
        setTimeout(() => this.router.navigate(['/login']), 700);
      },
      error: (err) => {
        this.error = err.error?.detail ?? 'Unable to create account.';
        this.loading = false;
      },
      complete: () => this.loading = false,
    });
  }
}
