import { create } from 'zustand';
import { adminAPI } from '../services/api';

export const useAdminStore = create((set, get) => ({
  drops: [],
  isLoading: false,
  error: null,

  createDrop: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const response = await adminAPI.createDrop(data);
      set({ isLoading: false });
      return response.data;
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Failed to create drop';
      set({ error: errorMsg, isLoading: false });
      throw error;
    }
  },

  updateDrop: async (id, data) => {
    set({ isLoading: true, error: null });
    try {
      const response = await adminAPI.updateDrop(id, data);
      set({ isLoading: false });
      return response.data;
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Failed to update drop';
      set({ error: errorMsg, isLoading: false });
      throw error;
    }
  },

  deleteDrop: async (id) => {
    set({ isLoading: true, error: null });
    try {
      await adminAPI.deleteDrop(id);
      set({ isLoading: false });
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Failed to delete drop';
      set({ error: errorMsg, isLoading: false });
      throw error;
    }
  },

  clearError: () => set({ error: null }),
}));
