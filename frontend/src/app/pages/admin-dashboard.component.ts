import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { finalize } from 'rxjs';
import { ApiService } from '../core/api.service';
import { AdminStats, User } from '../core/models';

@Component({
  selector: 'app-admin-dashboard',
  imports: [CommonModule, RouterLink],
  template: `<div class="heading"><div><small>ADMINISTRATION</small><h1>Admin center</h1><p>Global platform activity and user governance.</p></div><a routerLink="/users" class="primary">Manage users</a></div><p class="loading" *ngIf="loading">Loading administration data…</p><div *ngIf="!loading"><div class="stats"><article><span>Users</span><strong>{{ stats?.users ?? 0 }}</strong></article><article><span>All projects</span><strong>{{ stats?.projects ?? 0 }}</strong></article><article><span>Successful runs</span><strong>{{ stats?.successful_runs ?? 0 }}</strong></article><article><span>Failed runs</span><strong>{{ stats?.failed_runs ?? 0 }}</strong></article></div><article class="panel"><div class="panel-head"><div><h2>Registered users</h2><p>Accounts currently using the platform</p></div></div><div class="row" *ngFor="let user of users"><div><b>{{ user.username }}</b><small>{{ user.email }}</small></div><span class="role">{{ user.role }}</span><span [class.inactive]="!user.is_active">{{ user.is_active ? 'Active' : 'Inactive' }}</span></div><div class="empty" *ngIf="!users.length">No users found.</div></article></div><p class="error" *ngIf="error">{{ error }}</p>`,
  styles: [`.heading,.panel-head,.row{display:flex;align-items:center;justify-content:space-between}.heading{margin-bottom:28px}.heading small{color:#7068f4;font-weight:700;letter-spacing:1.5px;font-size:10px}.heading h1{margin:9px 0 0;font-size:25px}.heading p,.panel p{color:#9293a1;font-size:12px;margin:8px 0 0}.primary{background:#7068f4;color:#fff;text-decoration:none;padding:12px 15px;border-radius:7px;font-size:12px}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px}.stats article,.panel{background:#fff;border:1px solid #ededf3;border-radius:10px;padding:20px}.stats span{color:#9293a1;font-size:11px}.stats strong{display:block;font-size:28px;margin-top:15px}.row{border-top:1px solid #f0f0f4;padding:15px 0;justify-content:flex-start;gap:15px}.row>div{flex:1}.row small{display:block;color:#999aa7;font-size:10px;margin-top:4px}.role{color:#7068f4;font-size:11px;text-transform:uppercase}.inactive{color:#d65e6d}.empty{color:#9293a1;font-size:12px;padding:28px 0}.error{color:#d65e6d;font-size:12px;margin-top:15px}@media(max-width:700px){.stats{grid-template-columns:repeat(2,1fr)}.heading{align-items:flex-start;gap:15px;flex-direction:column}}`],
})
export class AdminDashboardComponent {
  private readonly api = inject(ApiService);
  private readonly changeDetector = inject(ChangeDetectorRef);
  users: User[] = [];
  stats?: AdminStats;
  error = '';
  loading = true;
  constructor() {
    let pending = 2;
    const loaded = () => { pending -= 1; if (pending === 0) this.loading = false; };
    this.api.users().pipe(finalize(loaded)).subscribe({
      next: users => { this.users = users; this.changeDetector.markForCheck(); },
      error: err => { this.error = this.formatError(err); this.changeDetector.markForCheck(); },
    });
    this.api.adminStats().pipe(finalize(loaded)).subscribe({
      next: stats => { this.stats = stats; this.changeDetector.markForCheck(); },
      error: err => { this.error = this.formatError(err); this.changeDetector.markForCheck(); },
    });
  }
  private formatError(err: { error?: { detail?: string | { msg?: string }[] } }) {
    const detail = err.error?.detail;
    return Array.isArray(detail) ? detail.map(item => item.msg || 'Invalid value').join(' ') : detail || 'Unable to load administration data.';
  }
}
