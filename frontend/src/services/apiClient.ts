import axios from 'axios';

const baseURL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export const apiClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const errorMsg =
      error.response?.data?.error?.message ||
      error.message ||
      'An unexpected error occurred while communicating with the forecast intelligence service.';
    console.error('API Client Error:', errorMsg, error.response?.data);
    return Promise.reject(new Error(errorMsg));
  }
);
