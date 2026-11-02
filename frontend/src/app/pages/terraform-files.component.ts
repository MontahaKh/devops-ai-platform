import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../core/api.service';
import { GeneratedFile, Run } from '../core/models';

@Component({
  selector: 'app-terraform-files', imports: [CommonModule, FormsModule],
  template: `
    <div class="heading"><div><h1>Terraform files</h1><p>Create, edit and review files attached to prepared runs.</p></div><button type="button" class="primary" (click)="showForm=!showForm">+ Add file</button></div>
    <form class="create" *ngIf="showForm" (ngSubmit)="create()">
      <select name="run" [(ngModel)]="runId" required><option [ngValue]="0" disabled>Choose a pending run</option><option *ngFor="let run of runs" [ngValue]="run.id">Run #{{run.id}} ({{run.status}})</option></select>
      <input name="path" [(ngModel)]="path" placeholder="main.tf" required>
      <textarea name="content" [(ngModel)]="content" placeholder="terraform { }" required></textarea>
      <button type="submit" class="primary" [disabled]="saving">{{saving ? 'Saving…' : 'Save file'}}</button>
    </form>
    <div class="error" *ngIf="error">{{error}}</div>
    <div class="grid">
      <article class="card" *ngFor="let file of files">
        <div class="card-head"><b>{{file.path}}</b><span>Run #{{file.run_id}}</span></div>
        <small>{{file.file_type}} · version {{file.version}}</small>
        <textarea *ngIf="editingId === file.id" [(ngModel)]="editingContent" class="editor"></textarea>
        <pre *ngIf="editingId !== file.id">{{file.content}}</pre>
        <div class="actions">
          <button type="button" *ngIf="editingId !== file.id" (click)="startEdit(file)">Edit</button>
          <button type="button" *ngIf="editingId === file.id" (click)="saveEdit(file)" [disabled]="saving">{{saving ? 'Saving…' : 'Save changes'}}</button>
          <button type="button" *ngIf="editingId === file.id" (click)="cancelEdit()">Cancel</button>
          <button type="button" class="danger" (click)="remove(file)">Delete</button>
        </div>
      </article>
    </div>
    <div class="empty" *ngIf="!files.length">No generated files found.</div>
  `,
  styles: [`
    .heading,.card-head,.actions{display:flex;align-items:center}.heading{justify-content:space-between;margin-bottom:24px}.heading h1{font-size:25px;margin:0}.heading p{color:#9293a1;font-size:12px}.primary{border:0;background:#7068f4;color:#fff;border-radius:7px;padding:11px 15px;cursor:pointer}.primary:disabled{opacity:.6}.create{background:#fff;border:1px solid #ededf3;border-radius:10px;padding:16px;display:grid;gap:10px;margin-bottom:20px}.create input,.create select,.create textarea,.editor{padding:10px;border:1px solid #dddde7;border-radius:6px;font:12px inherit}.create textarea{min-height:120px}.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}.card{background:#fff;border:1px solid #ededf3;border-radius:10px;padding:18px}.card-head{justify-content:space-between;gap:12px}.card-head span,.card small,.empty,.error{color:#9293a1;font-size:11px}.card small{display:block;margin-top:6px}.card pre,.editor{width:100%;box-sizing:border-box;min-height:150px;margin:14px 0 0}.card pre{background:#181923;color:#d8d8e2;padding:12px;overflow:auto;border-radius:6px;font:11px monospace;white-space:pre-wrap}.editor{resize:vertical}.actions{gap:10px;margin-top:12px}.actions button{border:0;background:none;color:#7068f4;cursor:pointer;font-size:11px}.actions button:disabled{opacity:.6}.actions .danger{color:#d26a76}.error{color:#d65e6d;margin-bottom:15px}@media(max-width:700px){.grid{grid-template-columns:1fr}}
  `],
})
export class TerraformFilesComponent {
  private readonly api = inject(ApiService);
  private readonly changeDetector = inject(ChangeDetectorRef);
  files: GeneratedFile[] = [];
  runs: Run[] = [];
  showForm = false;
  runId = 0;
  path = '';
  content = '';
  editingId?: number;
  editingContent = '';
  saving = false;
  error = '';

  constructor() {
    this.load();
    this.api.runs().subscribe({
      next: data => { this.runs = data.filter(run => run.status === 'pending'); this.changeDetector.markForCheck(); },
      error: err => { this.error = this.formatError(err, 'Unable to load pending runs.'); this.changeDetector.markForCheck(); },
    });
  }

  load() {
    this.api.files().subscribe({
      next: data => { this.files = data; this.changeDetector.markForCheck(); },
      error: err => { this.error = this.formatError(err, 'Unable to load Terraform files.'); this.changeDetector.markForCheck(); },
    });
  }

  create() {
    if (this.saving || !this.runId || !this.path.trim() || !this.content.trim()) return;
    this.saving = true;
    this.error = '';
    this.api.createFile({ run_id: this.runId, file_type: 'terraform', path: this.path.trim(), content: this.content, version: 1, is_user_edited: true }).subscribe({
      next: file => {
        this.files = [file, ...this.files];
        this.path = '';
        this.content = '';
        this.showForm = false;
        this.saving = false;
        this.changeDetector.markForCheck();
      },
      error: err => { this.error = this.formatError(err, 'The file was rejected by the backend.'); this.saving = false; this.changeDetector.markForCheck(); },
    });
  }

  startEdit(file: GeneratedFile) {
    this.editingId = file.id;
    this.editingContent = file.content;
  }

  cancelEdit() {
    this.editingId = undefined;
    this.editingContent = '';
  }

  saveEdit(file: GeneratedFile) {
    if (this.saving || !this.editingContent.trim()) return;
    this.saving = true;
    this.error = '';
    this.api.updateFile(file.id, { content: this.editingContent, version: file.version + 1, is_user_edited: true }).subscribe({
      next: updated => {
        this.files = this.files.map(item => item.id === updated.id ? updated : item);
        this.cancelEdit();
        this.saving = false;
        this.changeDetector.markForCheck();
      },
      error: err => { this.error = this.formatError(err, 'Unable to save the Terraform file.'); this.saving = false; this.changeDetector.markForCheck(); },
    });
  }

  remove(file: GeneratedFile) {
    if (!confirm(`Delete ${file.path}?`)) return;
    this.api.deleteFile(file.id).subscribe({
      next: () => { this.files = this.files.filter(item => item.id !== file.id); this.changeDetector.markForCheck(); },
      error: err => { this.error = this.formatError(err, 'Unable to delete file.'); this.changeDetector.markForCheck(); },
    });
  }

  private formatError(err: { error?: { detail?: string | { msg?: string }[] } }, fallback: string) {
    const detail = err.error?.detail;
    return Array.isArray(detail) ? detail.map(item => item.msg || 'Invalid value').join(' ') : detail || fallback;
  }
}
