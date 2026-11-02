import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ApiService } from '../core/api.service';
import { Run } from '../core/models';

@Component({
  selector: 'app-validation-logs',
  imports: [CommonModule, RouterLink],
  template: `
    <div class="heading">
      <div>
        <small>TOOLS</small>
        <h1>Validation logs</h1>
        <p>Select a run to inspect its Terraform validation output.</p>
      </div>
      <button class="refresh" (click)="load()">Refresh</button>
    </div>
    <div class="panel">
      <div class="row header">
        <span>Run</span><span>Status</span><span>Created</span><span>Action</span>
      </div>
      <div class="row" *ngFor="let run of runs">
        <strong>Run #{{ run.id }}</strong>
        <span class="status" [class]="run.status">{{ run.status }}</span>
        <span>{{ run.created_at | date:'short' }}</span>
        <a [routerLink]="['/runs', run.id, 'logs']">View logs →</a>
      </div>
      <div class="empty" *ngIf="!runs.length && !error">
        No runs are available. Create and execute a run first.
      </div>
    </div>
    <div class="error" *ngIf="error">{{ error }}</div>
  `,
  styles: [`
    .heading { display:flex; align-items:center; justify-content:space-between; margin-bottom:24px; }
    .heading small { color:#7068f4; font-size:10px; font-weight:700; letter-spacing:1.5px; }
    .heading h1 { font-size:25px; margin:9px 0 0; }
    .heading p { color:#9293a1; font-size:12px; margin:8px 0 0; }
    .refresh { background:#fff; border:1px solid #e1e1eb; border-radius:7px; color:#7068f4; cursor:pointer; font-size:11px; padding:10px 14px; }
    .panel { background:#fff; border:1px solid #ededf3; border-radius:10px; padding:0 20px; }
    .row { align-items:center; border-bottom:1px solid #f0f0f4; color:#686977; display:grid; font-size:11px; gap:16px; grid-template-columns:1fr 1fr 1fr 1fr; padding:16px 0; }
    .row:last-child { border-bottom:0; }
    .header { color:#999aa7; font-size:10px; font-weight:700; }
    .status { background:#f1f1fa; border-radius:5px; justify-self:start; padding:5px 8px; }
    .status.success { background:#e9f8f1; color:#45a878; }
    .status.failed { background:#fff0f1; color:#dd727c; }
    .status.pending { background:#fff5e9; color:#d3904b; }
    .status.running { background:#eeefff; color:#7068ed; }
    a { color:#7068f4; font-size:11px; text-decoration:none; }
    .empty, .error { color:#9293a1; font-size:12px; padding:22px 0; }
    .error { color:#d65e6d; padding-top:15px; }
    @media (max-width:700px) {
      .row { grid-template-columns:1fr 1fr; }
      .header { display:none; }
      .row span:nth-child(3) { display:none; }
    }
  `],
})
export class ValidationLogsComponent {
  private readonly api = inject(ApiService);
  private readonly changeDetector = inject(ChangeDetectorRef);
  runs: Run[] = [];
  error = '';

  constructor() {
    this.load();
  }

  load() {
    this.error = '';
    this.api.runs().subscribe({
      next: runs => { this.runs = runs; this.changeDetector.markForCheck(); },
      error: err => { this.error = err.error?.detail ?? 'Unable to load runs for validation logs.'; this.changeDetector.markForCheck(); },
    });
  }
}
