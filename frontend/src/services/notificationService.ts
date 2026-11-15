import { api } from './api';
import { AppNotification } from '../types';

export const notificationService = {
  async listNotifications(): Promise<{
    email_service_status: { provider: string; is_configured: boolean; mail_from: string };
    notifications: AppNotification[];
  }> {
    const res = await api.get('/notifications');
    return res.data.data;
  },

  async markRead(id: string): Promise<AppNotification> {
    const res = await api.patch(`/notifications/${id}/read`);
    return res.data.data;
  },

  async getPreferences() {
    const res = await api.get('/notifications/preferences');
    return res.data.data;
  },

  async updatePreferences(data: {
    email_medication_reminders?: boolean;
    email_missed_dose_alerts?: boolean;
    email_appointment_reminders?: boolean;
    email_daily_summary?: boolean;
  }) {
    const res = await api.put('/notifications/preferences', data);
    return res.data.data;
  },

  async sendTestEmail(email?: string) {
    const res = await api.post('/notifications/test-email', { email });
    return res.data;
  }
};
