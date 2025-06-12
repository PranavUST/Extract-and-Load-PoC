import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { SourceConfig } from './source-config';

describe('SourceConfig', () => {
  let component: SourceConfig;
  let fixture: ComponentFixture<SourceConfig>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReactiveFormsModule, HttpClientTestingModule, SourceConfig]
    }).compileComponents();
    fixture = TestBed.createComponent(SourceConfig);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
