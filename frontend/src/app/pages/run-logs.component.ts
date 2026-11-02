import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { ApiService } from '../core/api.service';
import { RunLogs } from '../core/models';

@Component({
  selector: 'app-run-logs', imports: [CommonModule],
  template: `<div class="heading"><div><h1>Run #{{runId}} logs</h1><p>Terraform validation output and execution diagnostics.</p></div><span class="status" *ngIf="logs" [class]="logs.status">{{logs.status}}</span></div><div class="panel" *ngFor="let validation of logs?.validations"><div class="panel-head"><h2>{{validation.command}}</h2><span>Exit code: {{validation.exit_code ?? '—'}}</span></div><p *ngIf="validation.message">{{validation.message}}</p><pre *ngIf="validation.stdout">{{validation.stdout}}</pre><pre class="stderr" *ngIf="validation.stderr">{{validation.stderr}}</pre></div><div class="empty" *ngIf="logs && !logs.validations.length">No validations have been recorded yet.</div><div class="error" *ngIf="error">{{error}}</div>`,
  styles: [`.heading{display:flex;justify-content:space-between;align-items:center;margin-bottom:24px}.heading h1{font-size:25px;margin:0}.heading p{color:#9293a1;font-size:12px}.status{padding:6px 9px;border-radius:5px;font-size:10px;background:#f1f1fa}.status.success{color:#45a878;background:#e9f8f1}.status.failed{color:#dd727c;background:#fff0f1}.panel{background:#fff;border:1px solid #ededf3;border-radius:10px;padding:18px;margin-bottom:14px}.panel-head{display:flex;justify-content:space-between}.panel h2{font-size:14px;margin:0}.panel-head span,.panel p{font-size:11px;color:#9293a1}.panel pre{background:#181923;color:#d8d8e2;border-radius:6px;padding:14px;overflow:auto;white-space:pre-wrap;font:11px monospace}.panel pre.stderr{color:#ffadb3}.empty,.error{color:#9293a1;font-size:12px}.error{color:#d65e6d}`],
})
export class RunLogsComponent {
  private readonly api = inject(ApiService); private readonly route = inject(ActivatedRoute); private readonly changeDetector = inject(ChangeDetectorRef); runId = Number(this.route.snapshot.paramMap.get('id')); logs?: RunLogs; error = '';
  constructor() {
    this.api.logs(this.runId).subscribe({
      next: data => { this.logs = data; this.changeDetector.markForCheck(); },
      error: err => { this.error = err.error?.detail ?? 'Unable to load run logs.'; this.changeDetector.markForCheck(); },
    });
  }
}
