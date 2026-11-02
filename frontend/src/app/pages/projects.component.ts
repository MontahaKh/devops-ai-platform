import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { finalize } from 'rxjs';
import { ApiService } from '../core/api.service';
import { Project } from '../core/models';

@Component({
  selector: 'app-projects', imports: [CommonModule, FormsModule],
  template: `<div class="heading"><div><h1>Projects</h1><p>Manage your infrastructure workspaces.</p></div><button type="button" class="primary" (click)="showForm=!showForm">+ New project</button></div><form class="create" *ngIf="showForm" (ngSubmit)="create()"><input name="name" [(ngModel)]="name" placeholder="Project name" required><input name="description" [(ngModel)]="description" placeholder="Description"><button type="submit" class="primary" [disabled]="saving">{{ saving ? 'Creating…' : 'Create' }}</button></form><div class="loading" *ngIf="loading">Loading projects…</div><div class="grid" *ngIf="!loading"><article class="card" *ngFor="let project of projects"><div class="card-head"><span class="icon">▦</span><button type="button" (click)="remove(project)">Delete</button></div><h2>{{project.name}}</h2><p>{{project.description || 'No description provided.'}}</p><small>Created {{project.created_at | date:'mediumDate'}}</small></article></div><div class="empty" *ngIf="!loading && !projects.length">No projects found.</div><div class="error" *ngIf="error">{{error}}</div>`,
  styles: [`.heading,.card-head,.create{display:flex;align-items:center;justify-content:space-between}.heading{margin-bottom:24px}.heading h1{margin:0;font-size:25px}.heading p,.card p{color:#9293a1;font-size:12px}.primary{border:0;background:#7068f4;color:#fff;border-radius:7px;padding:11px 15px;cursor:pointer}.create{justify-content:flex-start;gap:10px;background:#fff;border:1px solid #ededf3;padding:16px;border-radius:10px;margin-bottom:20px}.create input{padding:10px;border:1px solid #dddde7;border-radius:6px;flex:1}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.card{background:#fff;border:1px solid #ededf3;border-radius:10px;padding:20px}.card-head button{border:0;background:none;color:#d26a76;cursor:pointer;font-size:11px}.icon{background:#eeefff;color:#7068f4;padding:9px;border-radius:7px}.card h2{font-size:15px;margin:21px 0 8px}.card small,.empty{color:#999aa7;font-size:11px}.error{color:#d65e6d;font-size:12px;margin-top:15px}@media(max-width:700px){.grid{grid-template-columns:1fr}.create{align-items:stretch;flex-direction:column}.create input{width:100%}}`],
})
export class ProjectsComponent {
  private readonly api = inject(ApiService); private readonly changeDetector = inject(ChangeDetectorRef); projects: Project[] = []; showForm = false; name = ''; description = ''; error = ''; loading = true; saving = false;
  constructor() { this.load(); }
  load() {
    this.loading = true;
    this.api.projects().pipe(finalize(() => { this.loading = false; this.changeDetector.markForCheck(); })).subscribe({
      next: data => { this.projects = data; this.changeDetector.markForCheck(); },
      error: err => { this.error = this.formatError(err, 'Unable to load projects.'); this.changeDetector.markForCheck(); },
    });
  }
  create() {
    if (this.saving || !this.name.trim()) return;
    this.saving = true;
    this.error = '';
    this.api.createProject({ name: this.name.trim(), description: this.description.trim() }).subscribe({
      next: project => {
        this.projects = [project, ...this.projects];
        this.name = '';
        this.description = '';
        this.showForm = false;
      },
      error: err => this.error = this.formatError(err, 'Unable to create project.'),
      complete: () => this.saving = false,
    });
  }
  remove(project: Project) { if (!confirm(`Delete ${project.name}?`)) return; this.api.deleteProject(project.id).subscribe({ next: () => this.projects = this.projects.filter(item => item.id !== project.id), error: err => this.error = this.formatError(err, 'Unable to delete project.') }); }
  private formatError(err: { error?: { detail?: string | { msg?: string }[] } }, fallback: string) {
    const detail = err.error?.detail;
    return Array.isArray(detail) ? detail.map(item => item.msg || 'Invalid value').join(' ') : detail || fallback;
  }
}
