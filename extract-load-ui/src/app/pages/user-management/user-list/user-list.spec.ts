import { UserList } from './user-list';

describe('UserList', () => {
  let mockUserManagementService: any;
  let mockAuthService: any;
  let component: UserList;
  // A valid user object for tests
  const validUser = {
    id: 1,
    name: 'A',
    email: 'a@b.com',
    username: 'a',
    role: 'User' as 'User',
    last_login: null
  };

  beforeEach(() => {
    mockUserManagementService = {
      getUsers: jasmine.createSpy('getUsers'),
      updateUserRole: jasmine.createSpy('updateUserRole'),
      deleteUser: jasmine.createSpy('deleteUser')
    };
    mockAuthService = { getCurrentUser: () => ({ username: 'me' }) };
    component = new UserList(mockUserManagementService, mockAuthService);
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load users (success branch)', () => {
    const response = { success: true, users: [validUser] };
    mockUserManagementService.getUsers.and.returnValue({ subscribe: (handlers: any) => handlers.next(response) });
    component.loadUsers();
    expect(component.users.length).toBe(1);
    expect(component.loading).toBeFalse();
  });

  it('should load users (error branch)', () => {
    mockUserManagementService.getUsers.and.returnValue({ subscribe: (handlers: any) => handlers.error('fail') });
    spyOn(console, 'error');
    component.loadUsers();
    expect(component.loading).toBeFalse();
    expect(console.error).toHaveBeenCalled();
  });

  it('should update user role (success branch)', () => {
    const user = { ...validUser };
    mockUserManagementService.updateUserRole.and.returnValue({ subscribe: (handlers: any) => handlers.next({ success: true }) });
    spyOn(console, 'log');
    component.updateUserRole(user);
    expect(console.log).toHaveBeenCalledWith('User role updated successfully');
  });

  it('should update user role (error branch)', () => {
    const user = { ...validUser };
    mockUserManagementService.updateUserRole.and.returnValue({ subscribe: (handlers: any) => handlers.error('fail') });
    spyOn(console, 'error');
    spyOn(component, 'loadUsers');
    component.updateUserRole(user);
    expect(console.error).toHaveBeenCalled();
    expect(component.loadUsers).toHaveBeenCalled();
  });

  it('should delete user (confirm true, success branch)', () => {
    spyOn(window, 'confirm').and.returnValue(true);
    const user = { ...validUser };
    mockUserManagementService.deleteUser.and.returnValue({ subscribe: (handlers: any) => handlers.next({ success: true }) });
    spyOn(component, 'loadUsers');
    component.deleteUser(user);
    expect(component.loadUsers).toHaveBeenCalled();
  });

  it('should not delete user if confirm is false', () => {
    spyOn(window, 'confirm').and.returnValue(false);
    const user = { ...validUser };
    component.deleteUser(user);
    expect(mockUserManagementService.deleteUser).not.toHaveBeenCalled();
  });

  it('should handle delete user error branch', () => {
    spyOn(window, 'confirm').and.returnValue(true);
    const user = { ...validUser };
    mockUserManagementService.deleteUser.and.returnValue({ subscribe: (handlers: any) => handlers.error('fail') });
    spyOn(console, 'error');
    component.deleteUser(user);
    expect(console.error).toHaveBeenCalled();
  });

  it('should detect current user', () => {
    component.currentUsername = 'me';
    expect(component.isCurrentUser({ ...validUser, username: 'me' })).toBeTrue();
    expect(component.isCurrentUser({ ...validUser, username: 'notme' })).toBeFalse();
  });
});
