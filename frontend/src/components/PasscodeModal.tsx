import React, { useState } from 'react';
import { KeyRound, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { profileService } from '../services/profileService';
import { useAuth } from '../contexts/AuthContext';

interface PasscodeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export const PasscodeModal: React.FC<PasscodeModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [passcode, setPasscode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const { refreshUser } = useAuth();

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!passcode.trim()) return;

    setIsLoading(true);
    setError(null);
    setSuccessMsg(null);

    try {
      const profile = await profileService.redeemPasscode(passcode.trim().toUpperCase());
      setSuccessMsg(`Successfully connected to ${profile.full_name}'s healthcare profile!`);
      await refreshUser();
      setTimeout(() => {
        setPasscode('');
        onClose();
        if (onSuccess) onSuccess();
      }, 1500);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Invalid passcode or expired code.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="relative w-full max-w-md bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden">
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-5 text-white">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-white/10 rounded-xl">
              <KeyRound className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold">Connect Healthcare Profile</h3>
              <p className="text-xs text-blue-100">Enter your family or caretaker authorization passcode</p>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <p className="text-sm text-slate-600">
            Have an invitation code from an elderly family member or healthcare coordinator? Enter the 8-character passcode below (e.g. <strong>FAM-4310</strong> or <strong>CARE-7892</strong>).
          </p>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1.5">
              Authorization Passcode
            </label>
            <input
              type="text"
              value={passcode}
              onChange={(e) => setPasscode(e.target.value.toUpperCase())}
              placeholder="e.g. FAM-4310 or CARE-7892"
              className="w-full text-center text-xl font-mono uppercase tracking-widest font-bold px-4 py-3 border-2 border-slate-200 rounded-xl focus:border-blue-600 focus:outline-none focus:ring-4 focus:ring-blue-100 transition-all"
              required
              disabled={isLoading || Boolean(successMsg)}
            />
          </div>

          {error && (
            <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {successMsg && (
            <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-xl text-green-700 text-sm">
              <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
              <span>{successMsg}</span>
            </div>
          )}

          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              disabled={isLoading}
              className="px-4 py-2.5 text-sm font-semibold text-slate-600 hover:text-slate-800 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading || !passcode.trim() || Boolean(successMsg)}
              className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm rounded-xl shadow-md shadow-blue-500/20 disabled:opacity-50 transition flex items-center gap-2"
            >
              {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
              {isLoading ? 'Verifying...' : 'Authorize Access'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
