import React, { useEffect, useState } from 'react';
import { Loader2, AlertCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { dashboardService } from '../services/dashboardService';
import { SeniorDashboardView } from './dashboard/SeniorDashboardView';
import { FamilyDashboardView } from './dashboard/FamilyDashboardView';
import { CaretakerDashboardView } from './dashboard/CaretakerDashboardView';
import { PasscodeModal } from '../components/PasscodeModal';

export const DashboardPage: React.FC = () => {
  const { user, activeProfileId } = useAuth();
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isPasscodeOpen, setIsPasscodeOpen] = useState<boolean>(false);

  const fetchDashboard = async () => {
    if (!user) return;
    setIsLoading(true);
    setError(null);

    try {
      if (user.role === 'ELDERLY') {
        const data = await dashboardService.getElderlyDashboard(activeProfileId || undefined);
        setDashboardData(data);
      } else if (user.role === 'FAMILY') {
        const data = await dashboardService.getFamilyDashboard();
        setDashboardData(data);
      } else if (user.role === 'CARETAKER') {
        const data = await dashboardService.getCaretakerDashboard();
        setDashboardData(data);
      }
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to load dashboard metrics');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, [user?.role, activeProfileId]);

  if (isLoading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="w-10 h-10 animate-spin text-blue-600" />
          <p className="text-sm font-semibold text-slate-500">Retrieving real healthcare data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto my-12 p-6 bg-red-50 border border-red-200 rounded-3xl text-center">
        <AlertCircle className="w-10 h-10 text-red-600 mx-auto mb-2" />
        <h3 className="text-lg font-bold text-red-900">Dashboard Unavailable</h3>
        <p className="text-sm text-red-700 mt-1 mb-4">{error}</p>
        <button
          onClick={fetchDashboard}
          className="px-5 py-2.5 bg-red-600 text-white font-bold text-sm rounded-xl"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {user?.role === 'ELDERLY' && dashboardData && (
        <SeniorDashboardView data={dashboardData} onRefresh={fetchDashboard} />
      )}

      {user?.role === 'FAMILY' && dashboardData && (
        <FamilyDashboardView
          data={dashboardData}
          onRefresh={fetchDashboard}
          onOpenPasscode={() => setIsPasscodeOpen(true)}
        />
      )}

      {user?.role === 'CARETAKER' && dashboardData && (
        <CaretakerDashboardView
          data={dashboardData}
          onRefresh={fetchDashboard}
          onOpenPasscode={() => setIsPasscodeOpen(true)}
        />
      )}

      <PasscodeModal
        isOpen={isPasscodeOpen}
        onClose={() => setIsPasscodeOpen(false)}
        onSuccess={fetchDashboard}
      />
    </div>
  );
};
