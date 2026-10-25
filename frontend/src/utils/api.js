import axios from 'axios';

const BASE_URL = 'http://localhost:5000/api';
const apiClient = axios.create();

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (
      error.response?.status === 401 &&
      error.response?.data?.error === 'Token is invalid or expired'
    ) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.dispatchEvent(new Event('auth:expired'));
    }

    return Promise.reject(error);
  }
);

const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export const api = {
  register: (data) =>
    apiClient.post(`${BASE_URL}/register`, data),

  login: (data) =>
    apiClient.post(`${BASE_URL}/login`, data),

  predict: (data) =>
    apiClient.post(`${BASE_URL}/predict`, data, { headers: getAuthHeaders() }),

  explain: (data) =>
    apiClient.post(`${BASE_URL}/explain`, data, { headers: getAuthHeaders() }),

  chat: (data) =>
    apiClient.post(`${BASE_URL}/chat`, data, { headers: getAuthHeaders() }),

  train: () =>
    apiClient.post(`${BASE_URL}/train`, {}, { headers: getAuthHeaders() }),

  status: () =>
    apiClient.get(`${BASE_URL}/status`),

  uploadCSV: (formData) =>
    apiClient.post(`${BASE_URL}/upload-csv`, formData, {
      headers: { ...getAuthHeaders(), 'Content-Type': 'multipart/form-data' }
    }),
};
