import axios from 'axios';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// A dedicated client for long-running AI operations.
// Prevents normal API requests from being blocked by global slow timeouts.
export const aiApiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 90000, // 90s timeout specifically for backend LLM synthesis
});

const attachToken = (config: any) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
};

const handleAuthError = (error: any) => {
  if (error.response?.status === 401) {
    localStorage.removeItem('access_token');
  }
  return Promise.reject(error);
};

apiClient.interceptors.request.use(attachToken, (error) => Promise.reject(error));
apiClient.interceptors.response.use((response) => response, handleAuthError);

aiApiClient.interceptors.request.use(attachToken, (error) => Promise.reject(error));
aiApiClient.interceptors.response.use((response) => response, handleAuthError);
