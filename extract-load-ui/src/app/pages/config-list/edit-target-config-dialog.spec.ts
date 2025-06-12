import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { EditTargetConfigDialogComponent } from './edit-target-config-dialog';
import { NO_ERRORS_SCHEMA } from '@angular/core';

describe('EditTargetConfigDialogComponent', () => {
  let component: EditTargetConfigDialogComponent;
  let fixture: ComponentFixture<EditTargetConfigDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      providers: [
        { provide: MatDialogRef, useValue: {} },
        { provide: MAT_DIALOG_DATA, useValue: { name: 'Target1', type: 'Database' } }
      ],
      schemas: [NO_ERRORS_SCHEMA],
      imports: [EditTargetConfigDialogComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(EditTargetConfigDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
