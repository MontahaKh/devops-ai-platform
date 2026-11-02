import { Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../core/auth.service';
import { User } from '../core/models';

@Component({
  selector: 'app-shell',
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive],
  template: `
    <div class="app-shell">
      <aside class="sidebar">
        <div class="brand"><div class="brand-mark">D</div><div><strong>DevOps AI</strong><span>Platform</span></div></div>
        <div class="workspace-label">WORKSPACE</div>
        <nav>
          <a routerLink="/dashboard" routerLinkActive="active"><span>⌂</span>Dashboard</a>
          <a routerLink="/projects" routerLinkActive="active"><span>▦</span>Projects</a>
          <a routerLink="/pipelines" routerLinkActive="active"><span>◈</span>Pipelines</a>
          <a routerLink="/runs" routerLinkActive="active"><span>↻</span>Runs</a>
          <a routerLink="/terraform-files" routerLinkActive="active"><span>⌘</span>Terraform files</a>
          <a routerLink="/profile" routerLinkActive="active"><span>◯</span>My profile</a>
        </nav>
        <div class="workspace-label">TOOLS</div>
        <nav>
          <a routerLink="/validation-logs" routerLinkActive="active"><span>▤</span>Validation logs</a>
          <a *ngIf="user?.role === 'admin'" routerLink="/admin" routerLinkActive="active"><span>★</span>Admin center</a>
        </nav>
        <div class="sidebar-bottom"><button (click)="logout()"><span>↪</span>Sign out</button><div class="profile"><div class="avatar">{{ initials }}</div><div><strong>{{ user?.username || 'Workspace' }}</strong><small>{{ user?.role || 'Authenticated' }}</small></div></div></div>
      </aside>
      <main class="content"><header class="topbar"><span>Workspace <b>/</b> DevOps platform</span><button class="mobile-logout" (click)="logout()">Sign out</button></header><section class="page"><router-outlet /></section></main>
    </div>
  `,
  styles: [`
    :host { display:block; } .app-shell { min-height:100vh; display:flex; } .sidebar { width:248px; background:#12131c; color:#9293a1; padding:28px 16px 18px; display:flex; flex-direction:column; } .brand { display:flex; gap:11px; align-items:center; color:#fff; padding:0 12px 42px; }.brand-mark { background:#7068f4; color:white; display:grid; place-items:center; width:34px;height:34px;border-radius:9px;font-weight:800; }.brand strong,.brand span,.profile strong,.profile small { display:block; }.brand span { color:#747687;font-size:11px; }.workspace-label { color:#5f6170;font-size:10px;letter-spacing:1.3px;padding:0 13px 12px;margin-top:5px; }.sidebar nav { display:grid;gap:4px;margin-bottom:28px; }.sidebar a,.sidebar button { border:0;background:transparent;border-radius:8px;color:#9293a1;text-decoration:none;padding:11px 13px;display:flex;gap:12px;font:13px inherit;text-align:left;cursor:pointer; }.sidebar a.active,.sidebar a:hover,.sidebar button:hover { background:#252634;color:white; }.sidebar a span,.sidebar button span { width:16px;text-align:center;color:#a39dff; }.sidebar-bottom { margin-top:auto; }.profile { border-top:1px solid #292a35;padding:18px 10px 0;display:flex;gap:10px;align-items:center; }.avatar { background:#d5c2a9;color:#544a3d;border-radius:50%;width:31px;height:31px;display:grid;place-items:center;font-size:10px; }.profile strong { color:#dddde5;font-size:12px; }.profile small { color:#737484;font-size:10px;margin-top:3px; }.content { flex:1;min-width:0;background:#f7f7fb; }.topbar { background:#fff;border-bottom:1px solid #ececf2;height:70px;padding:0 42px;color:#8c8d9c;font-size:12px;display:flex;justify-content:space-between;align-items:center; }.topbar b { margin:0 12px;color:#d0d0d8; }.mobile-logout { border:0;background:none;color:#7068f4;cursor:pointer; }.page { padding:36px 42px 60px;max-width:1400px; } @media(max-width:700px){.sidebar{display:none}.topbar,.page{padding-left:18px;padding-right:18px}.page{padding-top:25px}}
  `],
})
export class ShellComponent {
  private readonly auth = inject(AuthService);
  user: User | null = null;
  get initials() { return (this.user?.username || 'U').slice(0, 2).toUpperCase(); }
  constructor() {
    this.auth.loadCurrentUser().subscribe({ next: user => this.user = user });
    this.auth.currentUser$.subscribe(user => this.user = user);
  }
  logout() { this.auth.logout(); }
}
