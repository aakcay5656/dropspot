import { create } from 'zustand';
import { authAPI } from '../services/api';

export const useAuthStore = create((set, get) => ({
  user: null,
  token: localStorage.getItem('token'),
  isLoading: false,
  error: null,

  signup: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const response = await authAPI.signup(email, password);
      const { access_token, user } = response.data;
      localStorage.setItem('token', access_token);
      set({ token: access_token, user, isLoading: false });
      return user;
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Signup failed';
      set({ error: errorMsg, isLoading: false });
      throw error;
    }
  },

  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const response = await authAPI.login(email, password);
      const { access_token, user } = response.data;
      localStorage.setItem('token', access_token);
      set({ token: access_token, user, isLoading: false });
      return user;
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Login failed';
      set({ error: errorMsg, isLoading: false });
      throw error;
    }
  },

  logout: () => {
    localStorage.removeItem('token');
    set({ token: null, user: null });
  },

  clearError: () => set({ error: null }),
}));
