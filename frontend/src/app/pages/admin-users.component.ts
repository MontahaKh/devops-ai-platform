import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../core/api.service';
import { User } from '../core/models';

@Component({
  selector: 'app-admin-users',
  imports: [CommonModule],
  template: `<div class="heading"><div><small>ADMINISTRATION</small><h1>User management</h1><p>Manage accounts and platform roles.</p></div></div><article class="panel"><div class="row header"><b>User</b><b>Role</b><b>Status</b><b>Actions</b></div><div class="row" *ngFor="let user of users"><div><b>{{ user.username }}</b><small>{{ user.email }}</small></div><select [value]="user.role" (change)="changeRole(user, $any($event.target).value)"><option value="user">User</option><option value="viewer">Viewer</option><option value="admin">Admin</option></select><span [class.inactive]="!user.is_active">{{ user.is_active ? 'Active' : 'Inactive' }}</span><span>{{ user.id === currentUserId ? 'Current account' : 'Role controlled by API' }}</span></div><div class="empty" *ngIf="!users.length">No users found.</div></article><p class="success" *ngIf="message">{{ message }}</p><p class="error" *ngIf="error">{{ error }}</p>`,
  styles: [`.heading{margin-bottom:28px}.heading small{color:#7068f4;font-weight:700;letter-spacing:1.5px;font-size:10px}.heading h1{margin:9px 0 0;font-size:25px}.heading p{color:#9293a1;font-size:12px}.panel{background:#fff;border:1px solid #ededf3;border-radius:10px;padding:20px}.row{display:grid;grid-template-columns:2fr 1fr 1fr 1.5fr;gap:15px;align-items:center;border-top:1px solid #f0f0f4;padding:15px 0;font-size:12px}.row.header{border-top:0;padding-top:0;color:#9293a1}.row small{display:block;color:#999aa7;font-size:10px;margin-top:4px}.row select{width:max-content;padding:6px;border:1px solid #dfe0ea;border-radius:6px}.inactive,.error{color:#d65e6d}.success{color:#319466;font-size:12px}.error{font-size:12px}.empty{color:#9293a1;font-size:12px;padding:28px 0}@media(max-width:700px){.row{grid-template-columns:1fr 1fr}}`],
})
export class AdminUsersComponent {
  private readonly api = inject(ApiService);
  users: User[] = [];
  currentUserId?: number;
  message = '';
  error = '';

  constructor() {
    this.api.users().subscribe({
      next: users => this.users = users,
      error: () => this.error = 'Unable to load users.',
    });
  }

  changeRole(user: User, role: string) {
    this.message = '';
    this.error = '';
    this.api.changeRole(user.id, role).subscribe({
      next: updated => {
        Object.assign(user, updated);
        this.message = `Role updated for ${user.username}.`;
      },
      error: err => this.error = err.error?.detail ?? 'Unable to update role.',
    });
  }
}
