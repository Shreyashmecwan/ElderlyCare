import { api } from './api';
import { User } from '../types';

export const authService = {
  async register(data: { email: string; password: string; full_name: string; role: string; phone_number?: string; timezone?: string }) {
    const res = await api.post('/auth/register', data);
    return res.data;
  },

  async login(data: { email: string; password: string }) {
    const res = await api.post('/auth/login', data);
    return res.data;
  },

  async getMe(): Promise<{ success: boolean; data: User }> {
    const res = await api.get('/auth/me');
    return res.data;
  },

  logout() {
    localStorage.removeItem('eldercare_token');
    localStorage.removeItem('eldercare_refresh_token');
    localStorage.removeItem('eldercare_user');
  }
};
