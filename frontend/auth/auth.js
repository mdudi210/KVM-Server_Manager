import { apiClient } from '@/config/api';
import { clearAuthState, markAuthenticated, shouldReuseAuthProbe } from './session';

export async function isAuthenticated(forceProbe = false) {
  if (!forceProbe && shouldReuseAuthProbe()) {
    return true;
  }

  try {
    await apiClient.get('/vm');
    markAuthenticated();
    return true;
  } catch (error) {
    if (error.response?.status === 401) {
      clearAuthState();
    }
    return false;
  }
}
