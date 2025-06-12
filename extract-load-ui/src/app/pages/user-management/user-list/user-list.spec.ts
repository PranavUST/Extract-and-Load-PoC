import { UserList } from './user-list';
describe('UserList', () => {
  it('should create', () => {
    const mockUserManagementService = {} as any;
    const mockAuthService = {} as any;
    expect(new UserList(mockUserManagementService, mockAuthService)).toBeTruthy();
  });
});
