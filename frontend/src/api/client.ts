import axios from 'axios';
import { toast } from 'sonner';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

export const aiApiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 90000,
});

const attachToken = (config: any) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
};

const handleApiError = (error: any) => {
  if (!error.response) {
    toast.error("Network error. Please check your connection.");
    return Promise.reject(error);
  }

  const { status } = error.response;

  if (status === 401) {
    localStorage.removeItem('access_token');
    // Only redirect if not already on login, and don't redirect if it was a /me check failure
    if (window.location.pathname !== '/login' && !error.config.url.includes('/auth/me')) {
      window.location.href = '/login';
    }
  } else if (status === 403) {
    toast.error("You do not have permission to perform this action.");
  } else if (status === 429) {
    toast.error("Too many requests. Please slow down.");
  } else if (status === 422) {
    toast.error("Invalid input parameters.");
  } else if (status >= 500) {
    toast.error("An internal server error occurred.");
  }

  return Promise.reject(error);
};

apiClient.interceptors.request.use(attachToken, (error) => Promise.reject(error));
apiClient.interceptors.response.use((response) => response, handleApiError);

aiApiClient.interceptors.request.use(attachToken, (error) => Promise.reject(error));
aiApiClient.interceptors.response.use((response) => response, handleApiError);

