import { create } from 'zustand';
import { dropsAPI, adminAPI } from '../services/api';

export const useDropStore = create((set, get) => ({
  drops: [],
  selectedDrop: null,
  isLoading: false,
  error: null,

  fetchDrops: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await dropsAPI.getDrops();
      set({ drops: response.data, isLoading: false });
    } catch (error) {
      set({ error: error.message, isLoading: false });
    }
  },

  fetchDrop: async (id) => {
    set({ isLoading: true, error: null });
    try {
      const response = await dropsAPI.getDrop(id);
      set({ selectedDrop: response.data, isLoading: false });
      return response.data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },

  joinWaitlist: async (id) => {
    try {
      const response = await dropsAPI.joinWaitlist(id);
      await get().fetchDrops();
      return response.data;
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Failed to join waitlist';
      set({ error: errorMsg });
      throw error;
    }
  },

  leaveWaitlist: async (id) => {
    try {
      await dropsAPI.leaveWaitlist(id);
      await get().fetchDrops();
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },

  claimDrop: async (id) => {
    try {
      const response = await dropsAPI.claimDrop(id);
      await get().fetchDrops();
      return response.data;
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Claim failed';
      set({ error: errorMsg });
      throw error;
    }
  },

  // Admin actions
  createDrop: async (data) => {
    try {
      const response = await adminAPI.createDrop(data);
      await get().fetchDrops();
      return response.data;
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Failed to create drop';
      set({ error: errorMsg });
      throw error;
    }
  },

  updateDrop: async (id, data) => {
    try {
      const response = await adminAPI.updateDrop(id, data);
      await get().fetchDrops();
      return response.data;
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Failed to update drop';
      set({ error: errorMsg });
      throw error;
    }
  },

  deleteDrop: async (id) => {
    try {
      await adminAPI.deleteDrop(id);
      await get().fetchDrops();
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Failed to delete drop';
      set({ error: errorMsg });
      throw error;
    }
  },

  clearError: () => set({ error: null }),
}));
