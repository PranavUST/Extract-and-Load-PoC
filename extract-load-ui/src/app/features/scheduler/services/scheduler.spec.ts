import { TestBed } from '@angular/core/testing';

import { Scheduler } from './scheduler';

describe('Scheduler', () => {
  let service: Scheduler;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Scheduler);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
