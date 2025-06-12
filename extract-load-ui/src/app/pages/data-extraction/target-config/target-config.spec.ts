import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { TargetConfig } from './target-config';

describe('TargetConfig', () => {
  let component: TargetConfig;
  let fixture: ComponentFixture<TargetConfig>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReactiveFormsModule, HttpClientTestingModule, TargetConfig]
    }).compileComponents();
    fixture = TestBed.createComponent(TargetConfig);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
