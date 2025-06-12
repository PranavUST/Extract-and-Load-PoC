import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TemplateList } from './template-list';
import { By } from '@angular/platform-browser';
describe('TemplateList', () => {
  let component: TemplateList;
  let fixture: ComponentFixture<TemplateList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TemplateList]
    }).compileComponents();
    fixture = TestBed.createComponent(TemplateList);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should have default templates', () => {
    expect(component.templates.length).toBeGreaterThan(0);
  });

  it('should delete a template', () => {
    const initialLength = component.templates.length;
    const toDelete = component.templates[0];
    component.deleteTemplate(toDelete);
    expect(component.templates.length).toBe(initialLength - 1);
    expect(component.templates.find(t => t.id === toDelete.id)).toBeUndefined();
  });

  it('should call alert on editTemplate', () => {
    spyOn(window, 'alert');
    component.editTemplate(component.templates[0]);
    expect(window.alert).toHaveBeenCalledWith(jasmine.stringMatching('Edit template'));
  });

  it('should call alert on createNewTemplate', () => {
    spyOn(window, 'alert');
    component.createNewTemplate();
    expect(window.alert).toHaveBeenCalledWith(jasmine.stringMatching('Create new template'));
  });
});
