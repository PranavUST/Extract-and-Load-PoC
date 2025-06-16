import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ApiService } from './api.service';
import { HttpClient } from '@angular/common/http';
import { of } from 'rxjs';

describe('ApiService', () => {
  let service: ApiService;
  let httpSpy: jasmine.SpyObj<HttpClient>;

  beforeEach(() => {
    httpSpy = jasmine.createSpyObj('HttpClient', [
      'post', 'get', 'put', 'delete'
    ]);
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [
        { provide: HttpClient, useValue: httpSpy }
      ]
    });
    service = TestBed.inject(ApiService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should call runPipeline', () => {
    httpSpy.post.and.returnValue(of({}));
    service.runPipeline({}).subscribe();
    expect(httpSpy.post).toHaveBeenCalled();
  });

  it('should call getPipelineStatus', () => {
    httpSpy.get.and.returnValue(of({}));
    service.getPipelineStatus().subscribe();
    expect(httpSpy.get).toHaveBeenCalled();
  });

  it('should call stopPipeline', () => {
    httpSpy.post.and.returnValue(of({}));
    service.stopPipeline().subscribe();
    expect(httpSpy.post).toHaveBeenCalled();
  });

  it('should call saveSourceConfig', () => {
    httpSpy.post.and.returnValue(of({}));
    service.saveSourceConfig({}).subscribe();
    expect(httpSpy.post).toHaveBeenCalled();
  });

  it('should call saveTargetConfig', () => {
    httpSpy.post.and.returnValue(of({}));
    service.saveTargetConfig({}).subscribe();
    expect(httpSpy.post).toHaveBeenCalled();
  });

  it('should call getUsers', () => {
    httpSpy.get.and.returnValue(of([]));
    service.getUsers().subscribe();
    expect(httpSpy.get).toHaveBeenCalledWith('http://localhost:5000/v1/data');
  });

  it('should call updateUser', () => {
    httpSpy.put.and.returnValue(of({}));
    service.updateUser({ id: 1 }).subscribe();
    expect(httpSpy.put).toHaveBeenCalledWith('http://localhost:5000/users/1', { id: 1 });
  });

  it('should call deleteUser', () => {
    httpSpy.delete.and.returnValue(of({}));
    service.deleteUser(1).subscribe();
    expect(httpSpy.delete).toHaveBeenCalledWith('http://localhost:5000/users/1');
  });
});
