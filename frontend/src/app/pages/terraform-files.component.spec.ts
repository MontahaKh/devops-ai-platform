import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { ApiService } from '../core/api.service';
import { GeneratedFile } from '../core/models';
import { TerraformFilesComponent } from './terraform-files.component';

const file: GeneratedFile = {
  id: 4,
  run_id: 8,
  file_type: 'terraform',
  path: 'main.tf',
  content: 'terraform {}',
  version: 1,
  is_user_edited: false,
  created_at: '2026-11-02T12:00:00Z',
};

describe('TerraformFilesComponent', () => {
  it('loads and saves an edited Terraform file', () => {
    const api = {
      files: () => of([file]),
      runs: () => of([]),
      updateFile: () => of({ ...file, content: 'terraform { required_version = ">= 1.0" }', version: 2, is_user_edited: true }),
    };

    TestBed.configureTestingModule({
      imports: [TerraformFilesComponent],
      providers: [{ provide: ApiService, useValue: api }],
    });
    const fixture = TestBed.createComponent(TerraformFilesComponent);
    const component = fixture.componentInstance;
    fixture.detectChanges();
    component.startEdit(file);
    component.editingContent = 'terraform { required_version = ">= 1.0" }';
    component.saveEdit(file);

    expect(component.files[0].version).toBe(2);
    expect(component.files[0].is_user_edited).toBe(true);
  });
});
