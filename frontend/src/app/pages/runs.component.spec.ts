import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { ApiService } from '../core/api.service';
import { Run } from '../core/models';
import { RunsComponent } from './runs.component';

const run: Run = {
  id: 8,
  pipeline_id: 3,
  status: 'pending',
  created_at: '2026-11-02T12:00:00Z',
  correlation_id: 'test-correlation',
  retry_count: 0,
  max_retries: 2,
  timeout_seconds: 300,
};

describe('RunsComponent', () => {
  const api = {
    runs: () => of([run]),
    pipelines: () => of([{ id: 3, name: 'Validation', project_id: 1, definition: {}, status: 'active' }]),
    createRun: (payload: object) => of({ ...run, id: 9, ...payload } as Run),
    executeRun: () => of({ ...run, status: 'success' } as Run),
    cancelRun: () => of({ ...run, status: 'cancelled' } as Run),
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RunsComponent],
      providers: [
        provideRouter([]),
        { provide: ApiService, useValue: api },
      ],
    }).compileComponents();
  });

  it('loads runs and pipelines', () => {
    const fixture = TestBed.createComponent(RunsComponent);
    fixture.detectChanges();

    expect(fixture.componentInstance.runs).toHaveLength(1);
    expect(fixture.componentInstance.pipelines[0].id).toBe(3);
  });

  it('creates a run and adds it to the list', () => {
    const fixture = TestBed.createComponent(RunsComponent);
    const component = fixture.componentInstance;
    component.pipelineId = 3;
    component.create();

    expect(component.runs[0].id).toBe(9);
    expect(component.showForm).toBe(false);
  });
});
