import { apiClient } from '@/config/api';

export async function login(username, password, authProvider = 'local') {
  const response = await apiClient.post('/login', {
    username,
    password,
    auth_provider: authProvider,
  });

  return response;
}
