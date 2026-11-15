import { api } from './api';
import { ElderlyProfile, ProfileMembership, Invitation } from '../types';

export const profileService = {
  async getMyProfiles(): Promise<ElderlyProfile[]> {
    const res = await api.get('/profiles');
    return res.data.data;
  },

  async getProfile(id: string): Promise<ElderlyProfile> {
    const res = await api.get(`/profiles/${id}`);
    return res.data.data;
  },

  async createProfile(data: Partial<ElderlyProfile>): Promise<ElderlyProfile> {
    const res = await api.post('/profiles', data);
    return res.data.data;
  },

  async updateProfile(id: string, data: Partial<ElderlyProfile>): Promise<ElderlyProfile> {
    const res = await api.put(`/profiles/${id}`, data);
    return res.data.data;
  },

  async listMembers(profileId: string): Promise<ProfileMembership[]> {
    const res = await api.get(`/profiles/${profileId}/members`);
    return res.data.data;
  },

  async revokeMember(profileId: string, membershipId: string): Promise<void> {
    await api.delete(`/profiles/${profileId}/members/${membershipId}`);
  },

  async createInvitation(profileId: string, data: { role: string; permission: string; relationship_title?: string; recipient_email?: string }): Promise<Invitation> {
    const res = await api.post(`/profiles/${profileId}/invitations`, data);
    return res.data.data;
  },

  async listInvitations(profileId: string): Promise<Invitation[]> {
    const res = await api.get(`/profiles/${profileId}/invitations`);
    return res.data.data;
  },

  async revokeInvitation(profileId: string, invitationId: string): Promise<void> {
    await api.delete(`/profiles/${profileId}/invitations/${invitationId}`);
  },

  async redeemPasscode(passcode: string): Promise<ElderlyProfile> {
    const res = await api.post('/profiles/join', { passcode });
    return res.data.data;
  }
};
