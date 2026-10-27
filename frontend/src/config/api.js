import axios from 'axios';

const trimTrailingSlash = (value) => value.replace(/\/+$/, '');

const getApiBaseUrl = () => {
  if (process.env.NODE_ENV === 'development') {
    return trimTrailingSlash(process.env.VUE_APP_API_URL || 'http://127.0.0.1:8000');
  }

  if (typeof window !== 'undefined') {
    return trimTrailingSlash(window.location.origin);
  }

  return 'http://127.0.0.1:8000';
};

export const API_BASE_URL = getApiBaseUrl();

export const buildApiUrl = (path) => {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL}${normalizedPath}`;
};

export const buildWsUrl = (path) => {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  const wsBase = API_BASE_URL.startsWith('https://')
    ? API_BASE_URL.replace('https://', 'wss://')
    : API_BASE_URL.replace('http://', 'ws://');
  return `${wsBase}${normalizedPath}`;
};

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  timeout: 15000,
  headers: {
    'X-Requested-With': 'XMLHttpRequest',
  },
});

export default {
  API_BASE_URL,
  buildApiUrl,
  buildWsUrl,
  apiClient,
};
