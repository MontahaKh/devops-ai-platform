import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { finalize, switchMap, takeWhile, timer } from 'rxjs';
import { ApiService } from '../core/api.service';
import { Pipeline, Run } from '../core/models';

@Component({
  selector: 'app-runs', imports: [CommonModule, FormsModule, RouterLink],
  template: `
    <div class="heading">
      <div><h1>Pipeline runs</h1><p>Prepare, execute and inspect your Terraform runs.</p></div>
      <button type="button" class="primary" (click)="showForm=!showForm">+ New run</button>
    </div>
    <form class="create" *ngIf="showForm" (ngSubmit)="create()">
      <select name="pipeline" [(ngModel)]="pipelineId" required>
        <option [ngValue]="0" disabled>Choose a pipeline</option>
        <option *ngFor="let pipeline of pipelines" [ngValue]="pipeline.id">{{pipeline.name}} (#{{pipeline.id}})</option>
      </select>
      <label>Retries<input name="retries" type="number" min="0" max="10" [(ngModel)]="maxRetries"></label>
      <label>Timeout (seconds)<input name="timeout" type="number" min="1" max="86400" [(ngModel)]="timeoutSeconds"></label>
      <button type="submit" class="primary" [disabled]="saving || !pipelineId">{{saving ? 'Creating…' : 'Create run'}}</button>
    </form>
    <div class="error" *ngIf="error">{{error}}</div>
    <div class="panel">
      <div class="row header"><span>Run</span><span>Pipeline</span><span>Status</span><span>Created</span><span>Actions</span></div>
      <div class="row" *ngFor="let run of runs">
        <b>#{{run.id}}</b><span>Pipeline #{{run.pipeline_id}}</span>
        <span class="status" [class]="run.status">{{run.status}}</span>
        <span>{{run.created_at | date:'short'}}</span>
        <span class="actions">
          <button type="button" *ngIf="run.status==='pending'" (click)="execute(run)" [disabled]="executingId === run.id">{{executingId === run.id ? 'Starting…' : 'Execute'}}</button>
          <button type="button" *ngIf="run.status==='pending'||run.status==='running'" (click)="cancel(run)">Cancel</button>
          <a [routerLink]="['/runs',run.id,'logs']">Logs</a>
        </span>
      </div>
      <div class="empty" *ngIf="!runs.length">No runs found.</div>
    </div>
  `,
  styles: [`
    .heading,.create,.row{display:flex;align-items:center}.heading{justify-content:space-between;margin-bottom:24px}.heading h1{font-size:25px;margin:0}.heading p{color:#9293a1;font-size:12px}.primary{border:0;background:#7068f4;color:#fff;border-radius:7px;padding:11px 15px;cursor:pointer}.primary:disabled{opacity:.6}.create{justify-content:flex-start;gap:12px;flex-wrap:wrap;background:#fff;border:1px solid #ededf3;padding:16px;border-radius:10px;margin-bottom:20px}.create select,.create input{padding:9px;border:1px solid #dddde7;border-radius:6px;background:#fff}.create label{display:flex;align-items:center;gap:6px;color:#686977;font-size:11px}.panel{background:#fff;border:1px solid #ededf3;border-radius:10px;padding:0 20px}.row{display:grid;grid-template-columns:.5fr 1.2fr .8fr 1fr 1.5fr;gap:12px;border-bottom:1px solid #f0f0f4;padding:16px 0;font-size:11px;color:#686977}.header{color:#999aa7;font-size:10px;font-weight:700}.status{justify-self:start;border-radius:5px;padding:5px 8px;background:#f1f1fa}.status.success{color:#45a878;background:#e9f8f1}.status.failed{color:#dd727c;background:#fff0f1}.status.pending{color:#d3904b;background:#fff5e9}.status.running{color:#7068ed;background:#eeefff}.actions{display:flex;gap:8px;align-items:center}.actions button,.actions a{border:0;background:none;color:#7068f4;cursor:pointer;text-decoration:none;font-size:10px}.actions button:disabled{opacity:.6}.empty,.error{color:#9293a1;font-size:12px;padding:22px 0}.error{color:#d65e6d;padding:0 0 15px}@media(max-width:700px){.header{display:none}.row{grid-template-columns:1fr 1fr;padding:14px 0}.row span:nth-child(2),.row span:nth-child(4){display:none}}
  `],
})
export class RunsComponent {
  private readonly api = inject(ApiService);
  private readonly changeDetector = inject(ChangeDetectorRef);
  runs: Run[] = [];
  pipelines: Pipeline[] = [];
  showForm = false;
  pipelineId = 0;
  maxRetries = 2;
  timeoutSeconds = 300;
  saving = false;
  executingId?: number;
  error = '';

  constructor() {
    this.load();
    this.api.pipelines().subscribe({
      next: data => { this.pipelines = data; this.changeDetector.markForCheck(); },
      error: err => { this.error = this.formatError(err, 'Unable to load pipelines.'); this.changeDetector.markForCheck(); },
    });
  }

  load() {
    this.api.runs().subscribe({
      next: data => { this.runs = data; this.changeDetector.markForCheck(); },
      error: err => { this.error = this.formatError(err, 'Unable to load runs.'); this.changeDetector.markForCheck(); },
    });
  }

  create() {
    if (this.saving || !this.pipelineId) return;
    this.saving = true;
    this.error = '';
    this.api.createRun({
      pipeline_id: this.pipelineId,
      max_retries: this.maxRetries,
      timeout_seconds: this.timeoutSeconds,
    }).pipe(finalize(() => { this.saving = false; this.changeDetector.markForCheck(); })).subscribe({
      next: run => {
        this.runs = [run, ...this.runs];
        this.showForm = false;
        this.pipelineId = 0;
        this.changeDetector.markForCheck();
      },
      error: err => { this.error = this.formatError(err, 'Unable to create run.'); this.changeDetector.markForCheck(); },
    });
  }

  execute(run: Run) {
    this.executingId = run.id;
    this.error = '';
    this.api.executeRun(run.id).pipe(finalize(() => { this.executingId = undefined; this.changeDetector.markForCheck(); })).subscribe({
      next: updated => {
        this.replace(updated);
        if (updated.status === 'running') this.watch(updated.id);
      },
      error: err => { this.error = this.formatError(err, 'Execution failed.'); this.changeDetector.markForCheck(); },
    });
  }

  cancel(run: Run) {
    this.api.cancelRun(run.id).subscribe({
      next: updated => this.replace(updated),
      error: err => { this.error = this.formatError(err, 'Cancellation failed.'); this.changeDetector.markForCheck(); },
    });
  }

  private watch(runId: number) {
    timer(1000, 2000).pipe(
      switchMap(() => this.api.runs()),
      takeWhile(runs => {
        const current = runs.find(run => run.id === runId);
        return Boolean(current && (current.status === 'pending' || current.status === 'running'));
      }, true),
    ).subscribe({
      next: runs => { this.runs = runs; this.changeDetector.markForCheck(); },
      error: err => { this.error = this.formatError(err, 'Unable to refresh run status.'); this.changeDetector.markForCheck(); },
    });
  }

  private replace(updated: Run) {
    this.runs = this.runs.map(item => item.id === updated.id ? updated : item);
    this.changeDetector.markForCheck();
  }

  private formatError(err: { error?: { detail?: string | { msg?: string }[] } }, fallback: string) {
    const detail = err.error?.detail;
    return Array.isArray(detail) ? detail.map(item => item.msg || 'Invalid value').join(' ') : detail || fallback;
  }
}
