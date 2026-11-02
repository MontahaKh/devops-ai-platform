import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../core/api.service';
import { AuthService } from '../core/auth.service';
import { User } from '../core/models';

@Component({
  selector: 'app-profile',
  imports: [CommonModule, FormsModule],
  template: `<div class="heading"><div><small>ACCOUNT</small><h1>My profile</h1><p>Manage your personal account details.</p></div></div><article class="card" *ngIf="user"><div class="identity"><div class="avatar">{{ user.username.slice(0, 2).toUpperCase() }}</div><div><h2>{{ user.username }}</h2><span class="role">{{ user.role }}</span></div></div><form (ngSubmit)="save()"><label>Username<input name="username" [(ngModel)]="username" required minlength="3" maxlength="50"></label><label>Email<input name="email" [(ngModel)]="email" required type="email"></label><label>New password <small>(leave blank to keep current password)</small><input name="password" [(ngModel)]="password" type="password" minlength="8"></label><button class="primary" [disabled]="saving">{{ saving ? 'Saving…' : 'Save changes' }}</button><p class="success" *ngIf="message">{{ message }}</p></form></article><p class="loading" *ngIf="!user && !error">Loading profile…</p><p class="error" *ngIf="error">{{ error }}</p>`,
  styles: [`.heading small{color:#7068f4;font-weight:700;letter-spacing:1.5px;font-size:10px}.heading h1{margin:9px 0 0;font-size:25px}.heading p{color:#9293a1;font-size:12px}.card{max-width:620px;background:#fff;border:1px solid #ededf3;border-radius:10px;padding:24px}.identity{display:flex;align-items:center;gap:14px;border-bottom:1px solid #eeeef4;padding-bottom:20px;margin-bottom:20px}.avatar{width:44px;height:44px;border-radius:50%;display:grid;place-items:center;background:#d5c2a9;color:#544a3d;font-weight:700}.identity h2{margin:0 0 5px;font-size:18px}.role{color:#7068f4;font-size:11px;text-transform:uppercase}label{display:block;color:#656675;font-size:12px;margin:17px 0}label small{color:#999aa7}input{display:block;width:100%;box-sizing:border-box;margin-top:7px;padding:11px;border:1px solid #dfe0ea;border-radius:7px}.primary{background:#7068f4;color:#fff;border:0;border-radius:7px;padding:11px 15px;cursor:pointer}.primary:disabled{opacity:.6}.success{color:#319466;font-size:12px}.error{color:#d65e6d;font-size:12px}`],
})
export class ProfileComponent {
  private readonly auth = inject(AuthService);
  private readonly api = inject(ApiService);
  private readonly changeDetector = inject(ChangeDetectorRef);
  user?: User;
  loading = true;
  username = '';
  email = '';
  password = '';
  saving = false;
  message = '';
  error = '';

  constructor() {
    const cachedUser = this.auth.currentUser();
    if (cachedUser) this.setUser(cachedUser);
    this.auth.loadCurrentUser().subscribe({
      next: user => this.setUser(user),
      error: () => {
        this.loading = false;
        this.error = 'Unable to load your profile. Please sign in again.';
        this.changeDetector.markForCheck();
      },
    });
  }

  private setUser(user: User) {
    this.user = user;
    this.username = user.username;
    this.email = user.email;
    this.loading = false;
    this.changeDetector.markForCheck();
  }

  save() {
    if (!this.user) return;
    this.saving = true;
    this.message = '';
    this.error = '';
    const payload = { username: this.username, email: this.email, ...(this.password ? { password: this.password } : {}) };
    this.api.updateUser(this.user.id, payload).subscribe({
      next: user => {
        this.user = user;
        this.password = '';
        this.auth.setCurrentUser(user);
        this.message = 'Profile updated.';
        this.changeDetector.markForCheck();
      },
      error: err => { this.error = err.error?.detail ?? 'Unable to update your profile.'; this.changeDetector.markForCheck(); },
      complete: () => { this.saving = false; this.changeDetector.markForCheck(); },
    });
  }
}
