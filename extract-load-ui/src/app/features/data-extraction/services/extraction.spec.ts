import { TestBed } from '@angular/core/testing';

import { Extraction } from './extraction.component';

describe('Extraction', () => {
  let service: Extraction;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Extraction);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
