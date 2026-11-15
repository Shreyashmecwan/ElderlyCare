import React, { useEffect, useState } from 'react';
import { 
  Users, 
  KeyRound, 
  Plus, 
  Trash2, 
  Copy, 
  Check, 
  ShieldCheck, 
  Clock, 
  X, 
  Loader2,
  Mail,
  UserPlus
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { profileService } from '../services/profileService';
import { ProfileMembership, Invitation } from '../types';

export const CareCirclePage: React.FC = () => {
  const { activeProfileId, user } = useAuth();
  const [members, setMembers] = useState<ProfileMembership[]>([]);
  const [invitations, setInvitations] = useState<Invitation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isInviteModalOpen, setIsInviteModalOpen] = useState(false);
  const [copiedCode, setCopiedCode] = useState<string | null>(null);

  // Invite Form
  const [role, setRole] = useState<'FAMILY' | 'CARETAKER'>('FAMILY');
  const [relationship, setRelationship] = useState('');
  const [permission, setPermission] = useState<'FULL_ACCESS' | 'VIEW_ONLY'>('FULL_ACCESS');
  const [recipientEmail, setRecipientEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchCircleData = async () => {
    if (!activeProfileId) return;
    setIsLoading(true);
    try {
      const [membersData, invitesData] = await Promise.all([
        profileService.listMembers(activeProfileId),
        profileService.listInvitations(activeProfileId)
      ]);
      setMembers(membersData);
      setInvitations(invitesData);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCircleData();
  }, [activeProfileId]);

  const handleCreateInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeProfileId) return;

    setIsSubmitting(true);
    try {
      await profileService.createInvitation(activeProfileId, {
        role,
        permission,
        relationship_title: relationship,
        recipient_email: recipientEmail
      });
      setIsInviteModalOpen(false);
      setRelationship('');
      setRecipientEmail('');
      fetchCircleData();
    } catch (err: any) {
      alert(err.response?.data?.error?.message || 'Failed to generate invitation');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRevokeMember = async (membershipId: string) => {
    if (!activeProfileId || !confirm('Are you sure you want to revoke this person’s access to the healthcare profile?')) return;
    try {
      await profileService.revokeMember(activeProfileId, membershipId);
      fetchCircleData();
    } catch (err: any) {
      alert(err.response?.data?.error?.message || 'Failed to revoke member');
    }
  };

  const handleRevokeInvite = async (inviteId: string) => {
    if (!activeProfileId) return;
    try {
      await profileService.revokeInvitation(activeProfileId, inviteId);
      fetchCircleData();
    } catch (err: any) {
      alert(err.response?.data?.error?.message || 'Failed to revoke passcode');
    }
  };

  const copyToClipboard = (code: string) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(code);
    setTimeout(() => setCopiedCode(null), 2500);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Care Circle & Access Permissions</h1>
          <p className="text-slate-600 font-medium">Control who can manage medications, log doses, and receive alerts</p>
        </div>

        <button
          onClick={() => setIsInviteModalOpen(true)}
          className="px-5 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm rounded-2xl shadow-lg shadow-blue-500/20 transition flex items-center gap-2 self-start sm:self-auto"
        >
          <UserPlus className="w-5 h-5" />
          <span>Generate Invite Passcode</span>
        </button>
      </div>

      {isLoading ? (
        <div className="py-20 text-center">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto" />
          <p className="text-sm font-semibold text-slate-500 mt-2">Loading Care Circle members...</p>
        </div>
      ) : (
        <>
          {/* Active Members Grid */}
          <div>
            <h2 className="text-xl font-black text-slate-900 mb-4 flex items-center gap-2">
              <Users className="w-5 h-5 text-blue-600" />
              <span>Authorized Care Circle Members</span>
            </h2>

            {members.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {members.map((m) => (
                  <div key={m.id} className="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm flex flex-col justify-between">
                    <div>
                      <div className="flex items-start justify-between gap-3 mb-2">
                        <div>
                          <h3 className="text-xl font-bold text-slate-900">{m.user_name || 'Caregiver'}</h3>
                          <p className="text-xs text-slate-500">{m.user_email}</p>
                        </div>
                        <span className="px-3 py-1 bg-blue-50 text-blue-800 text-xs font-bold rounded-full">
                          {m.role}
                        </span>
                      </div>

                      <div className="mt-4 p-3 bg-slate-50 rounded-2xl space-y-1.5 text-xs">
                        <div className="flex justify-between text-slate-600">
                          <span>Relationship:</span>
                          <strong className="text-slate-900">{m.relationship_title || 'Authorized Member'}</strong>
                        </div>
                        <div className="flex justify-between text-slate-600">
                          <span>Permission:</span>
                          <strong className={m.permission === 'FULL_ACCESS' ? 'text-emerald-700' : 'text-slate-700'}>
                            {m.permission}
                          </strong>
                        </div>
                      </div>
                    </div>

                    <div className="pt-4 mt-4 border-t border-slate-100 flex justify-end">
                      <button
                        onClick={() => handleRevokeMember(m.id)}
                        className="text-xs font-bold text-red-600 hover:text-red-700 flex items-center gap-1 hover:underline"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                        <span>Revoke Access</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-white border border-slate-200 rounded-3xl p-8 text-center text-slate-500 text-sm">
                No external caregivers or family members linked yet.
              </div>
            )}
          </div>

          {/* Active Invitations & Passcodes */}
          <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 shadow-sm">
            <h2 className="text-xl font-black text-slate-900 mb-2 flex items-center gap-2">
              <KeyRound className="w-5 h-5 text-indigo-600" />
              <span>Active Invitation Passcodes</span>
            </h2>
            <p className="text-xs text-slate-500 mb-6">
              Share these secure passcodes with trusted family members or caretakers to grant them access.
            </p>

            {invitations.length > 0 ? (
              <div className="divide-y divide-slate-100">
                {invitations.map((inv) => {
                  const isPending = inv.status === 'PENDING';
                  return (
                    <div key={inv.id} className="py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                      <div className="flex items-center gap-4">
                        <div className="px-4 py-2.5 bg-indigo-50 border border-indigo-200 rounded-2xl font-mono text-lg font-black text-indigo-900 tracking-wider">
                          {inv.passcode}
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-slate-900 text-sm">
                              Role: {inv.role} ({inv.relationship_title || 'Caregiver'})
                            </span>
                            <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-md font-semibold">
                              {inv.permission}
                            </span>
                          </div>
                          <p className="text-xs text-slate-500 mt-0.5">
                            Expires: {new Date(inv.expires_at).toLocaleDateString()} • Status: <strong className="uppercase">{inv.status}</strong>
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        {isPending && (
                          <>
                            <button
                              onClick={() => copyToClipboard(inv.passcode)}
                              className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs rounded-xl flex items-center gap-1.5 transition"
                            >
                              {copiedCode === inv.passcode ? <Check className="w-4 h-4 text-emerald-600" /> : <Copy className="w-4 h-4" />}
                              <span>{copiedCode === inv.passcode ? 'Copied!' : 'Copy Code'}</span>
                            </button>
                            <button
                              onClick={() => handleRevokeInvite(inv.id)}
                              className="p-1.5 text-slate-400 hover:text-red-600 rounded-xl"
                              title="Revoke Passcode"
                            >
                              <X className="w-5 h-5" />
                            </button>
                          </>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-slate-500 text-sm">No active invitations or passcodes right now.</p>
            )}
          </div>
        </>
      )}

      {/* Generate Invitation Modal */}
      {isInviteModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 overflow-y-auto">
          <div className="relative w-full max-w-lg bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden my-8">
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-5 text-white flex items-center justify-between">
              <h3 className="text-xl font-bold flex items-center gap-2">
                <KeyRound className="w-6 h-6" />
                <span>Generate Invitation Passcode</span>
              </h3>
              <button onClick={() => setIsInviteModalOpen(false)} className="text-white/80 hover:text-white">
                <X className="w-6 h-6" />
              </button>
            </div>

            <form onSubmit={handleCreateInvite} className="p-6 space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Recipient Role *
                </label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => setRole('FAMILY')}
                    className={`py-2.5 px-4 rounded-xl border text-sm font-bold transition ${
                      role === 'FAMILY' ? 'border-blue-600 bg-blue-50 text-blue-900' : 'border-slate-200 text-slate-700'
                    }`}
                  >
                    Family Member
                  </button>
                  <button
                    type="button"
                    onClick={() => setRole('CARETAKER')}
                    className={`py-2.5 px-4 rounded-xl border text-sm font-bold transition ${
                      role === 'CARETAKER' ? 'border-blue-600 bg-blue-50 text-blue-900' : 'border-slate-200 text-slate-700'
                    }`}
                  >
                    Professional Caretaker
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Relationship or Job Title
                </label>
                <input
                  type="text"
                  value={relationship}
                  onChange={(e) => setRelationship(e.target.value)}
                  placeholder="e.g. Daughter, Son, Home Health Nurse"
                  className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-semibold"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Access Permission Level
                </label>
                <select
                  value={permission}
                  onChange={(e) => setPermission(e.target.value as any)}
                  className="w-full px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-bold text-slate-700"
                >
                  <option value="FULL_ACCESS">FULL_ACCESS (Can manage meds, log doses, edit appointments)</option>
                  <option value="VIEW_ONLY">VIEW_ONLY (Can view schedules and adherence history)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Recipient Email (Optional)
                </label>
                <input
                  type="email"
                  value={recipientEmail}
                  onChange={(e) => setRecipientEmail(e.target.value)}
                  placeholder="name@example.com (optional)"
                  className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setIsInviteModalOpen(false)}
                  className="px-4 py-2.5 text-sm font-semibold text-slate-600 hover:text-slate-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm rounded-xl shadow-md transition flex items-center gap-2"
                >
                  {isSubmitting && <Loader2 className="w-4 h-4 animate-spin" />}
                  <span>Generate Code</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
