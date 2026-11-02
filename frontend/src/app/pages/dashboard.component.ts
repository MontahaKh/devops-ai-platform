import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { finalize } from 'rxjs';
import { ApiService } from '../core/api.service';
import { AuthService } from '../core/auth.service';
import { Pipeline, Project, Run } from '../core/models';

@Component({
  selector: 'app-dashboard',
  imports: [CommonModule, RouterLink],
  template: `<div class="heading"><div><small>OVERVIEW</small><h1>Infrastructure overview</h1><p>Live data from your DevOps workspace.</p></div><a routerLink="/projects" class="primary">Manage projects</a></div><div class="stats"><article><span>Projects</span><strong>{{ projects.length }}</strong></article><article><span>Pipelines</span><strong>{{ pipelines.length }}</strong></article><article><span>Successful runs</span><strong>{{ successCount }}</strong></article><article><span>Failed runs</span><strong>{{ failedCount }}</strong></article></div><article class="panel"><div class="panel-head"><div><h2>Recent runs</h2><p>Latest execution activity</p></div><a routerLink="/runs">View all →</a></div><div class="empty" *ngIf="!runs.length">No runs found. Create a pipeline and run to see activity.</div><div class="row" *ngFor="let run of runs.slice(0,6)"><span class="dot" [class]="run.status"></span><div><b>Run #{{run.id}}</b><small>Pipeline #{{run.pipeline_id}}</small></div><span class="status" [class]="run.status">{{run.status}}</span><a [routerLink]="['/runs',run.id,'logs']">Logs →</a></div></article><div class="error" *ngIf="error">{{error}}</div>`,
  styles: [`.heading,.panel-head,.row{display:flex;align-items:center;justify-content:space-between}.heading{margin-bottom:28px}.heading small{color:#7068f4;font-weight:700;letter-spacing:1.5px;font-size:10px}.heading h1{margin:9px 0 0;font-size:25px}.heading p,.panel p{color:#9293a1;font-size:12px;margin:8px 0 0}.primary{background:#7068f4;color:#fff;text-decoration:none;padding:12px 15px;border-radius:7px;font-size:12px}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px}.stats article,.panel{background:#fff;border:1px solid #ededf3;border-radius:10px;padding:20px}.stats span{color:#9293a1;font-size:11px}.stats strong{display:block;font-size:28px;margin-top:15px}.panel h2{font-size:14px;margin:0}.panel-head a,.row a{color:#7068f4;font-size:11px;text-decoration:none}.row{border-top:1px solid #f0f0f4;padding:15px 0;justify-content:flex-start;gap:12px}.row>div{flex:1}.row small{display:block;color:#999aa7;font-size:10px;margin-top:4px}.dot{width:7px;height:7px;border-radius:50%}.dot.success{background:#52bd8c}.dot.failed{background:#e77b83}.dot.pending{background:#e7a35b}.dot.running{background:#7068f4}.status{font-size:10px;padding:5px 8px;border-radius:5px;background:#f1f1fa}.status.success{color:#45a878;background:#e9f8f1}.status.failed{color:#dd727c;background:#fff0f1}.empty{color:#9293a1;font-size:12px;padding:28px 0}.error{color:#d65e6d;font-size:12px;margin-top:15px}@media(max-width:700px){.stats{grid-template-columns:repeat(2,1fr)}.heading{align-items:flex-start;gap:15px;flex-direction:column}}`],
})
export class DashboardComponent {
  private readonly api = inject(ApiService); projects: Project[] = []; pipelines: Pipeline[] = []; runs: Run[] = []; error = '';
  private readonly auth = inject(AuthService);
  private readonly changeDetector = inject(ChangeDetectorRef);
  private readonly router = inject(Router);
  get successCount() { return this.runs.filter(r => r.status === 'success').length; } get failedCount() { return this.runs.filter(r => r.status === 'failed').length; }
  loading = true;
  constructor() {
    this.auth.loadCurrentUser().subscribe({
      next: user => {
        if (user.role === 'admin') {
          this.router.navigate(['/admin']);
          return;
        }
        this.api.projects().subscribe({ next: data => { this.projects = data; this.changeDetector.markForCheck(); }, error: err => { this.error = this.formatError(err); this.changeDetector.markForCheck(); } });
        this.api.pipelines().subscribe({ next: data => { this.pipelines = data; this.changeDetector.markForCheck(); }, error: err => { this.error = this.formatError(err); this.changeDetector.markForCheck(); } });
        this.api.runs().pipe(finalize(() => this.loading = false)).subscribe({
          next: data => { this.runs = data; this.changeDetector.markForCheck(); },
          error: err => { this.error = this.formatError(err); this.changeDetector.markForCheck(); },
        });
      },
      error: err => {
        this.loading = false;
        this.error = this.formatError(err);
      },
    });
  }
  private formatError(err: { error?: { detail?: string | { msg?: string }[] } }) {
    const detail = err.error?.detail;
    return Array.isArray(detail) ? detail.map(item => item.msg || 'Invalid value').join(' ') : detail || 'Unable to load dashboard data.';
  }
}
