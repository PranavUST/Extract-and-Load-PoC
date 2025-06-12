import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { EditSourceConfigDialogComponent } from './edit-source-config-dialog';
import { NO_ERRORS_SCHEMA } from '@angular/core';

describe('EditSourceConfigDialogComponent', () => {
  let component: EditSourceConfigDialogComponent;
  let fixture: ComponentFixture<EditSourceConfigDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      providers: [
        { provide: MatDialogRef, useValue: {} },
        { provide: MAT_DIALOG_DATA, useValue: { name: 'Test', type: 'api' } }
      ],
      schemas: [NO_ERRORS_SCHEMA],
      imports: [EditSourceConfigDialogComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(EditSourceConfigDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
