import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Token ekle
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - Error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth endpoints
export const authAPI = {
  signup: (email, password) => api.post('/auth/signup', { email, password }),
  login: (email, password) => api.post('/auth/login', { email, password }),
};

// Drops endpoints
export const dropsAPI = {
  getDrops: (params) => api.get('/drops', { params }),
  getDrop: (id) => api.get(`/drops/${id}`),
  joinWaitlist: (id) => api.post(`/drops/${id}/join`, { request_time_ms: Date.now() }),
  leaveWaitlist: (id) => api.post(`/drops/${id}/leave`),
  claimDrop: (id) => api.post(`/drops/${id}/claim`),
};

// Admin endpoints
export const adminAPI = {
  createDrop: (data) => api.post('/admin/drops', data),
  updateDrop: (id, data) => api.put(`/admin/drops/${id}`, data),
  deleteDrop: (id) => api.delete(`/admin/drops/${id}`),
};

export default api;
