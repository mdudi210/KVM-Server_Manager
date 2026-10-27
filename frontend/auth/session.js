const authState = {
  authenticated: false,
  user: {
    username: 'User',
    role: 'user',
    id: null,
    authProvider: 'local',
  },
  lastAuthCheckMs: 0,
};

const AUTH_CHECK_TTL_MS = 15000;

export function setAuthFromLogin(payload = {}) {
  authState.authenticated = true;
  authState.user = {
    username: payload.username || 'User',
    role: payload.role || 'user',
    id: payload.id || null,
    authProvider: payload.auth_provider || 'local',
  };
  authState.lastAuthCheckMs = Date.now();
}

export function markAuthenticated() {
  authState.authenticated = true;
  authState.lastAuthCheckMs = Date.now();
}

export function clearAuthState() {
  authState.authenticated = false;
  authState.user = {
    username: 'User',
    role: 'user',
    id: null,
    authProvider: 'local',
  };
  authState.lastAuthCheckMs = 0;
}

export function getAuthState() {
  return authState;
}

export function shouldReuseAuthProbe() {
  return (
    authState.authenticated &&
    authState.lastAuthCheckMs > 0 &&
    Date.now() - authState.lastAuthCheckMs < AUTH_CHECK_TTL_MS
  );
}
