import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  Heart, 
  Pill, 
  Calendar, 
  BarChart2, 
  Bell, 
  Users, 
  LogOut, 
  KeyRound, 
  Eye, 
  Type, 
  ChevronDown,
  ShieldCheck
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useAccessibility } from '../contexts/AccessibilityContext';
import { PasscodeModal } from './PasscodeModal';

export const Navbar: React.FC = () => {
  const { user, logout, activeProfileId, setActiveProfileId } = useAuth();
  const { highContrast, toggleHighContrast, largeText, toggleLargeText } = useAccessibility();
  const [isPasscodeOpen, setIsPasscodeOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navLinks = [
    { name: 'Dashboard', path: '/dashboard', icon: Heart },
    { name: 'Medications', path: '/medications', icon: Pill },
    { name: 'Appointments', path: '/appointments', icon: Calendar },
    { name: 'Adherence', path: '/adherence', icon: BarChart2 },
    { name: 'Care Circle', path: '/care-circle', icon: Users },
    { name: 'Notifications', path: '/notifications', icon: Bell },
  ];

  const getRoleBadge = (role?: string) => {
    switch (role) {
      case 'ELDERLY':
        return <span className="bg-emerald-100 text-emerald-800 text-xs px-2.5 py-1 rounded-full font-bold uppercase tracking-wider">Senior</span>;
      case 'FAMILY':
        return <span className="bg-blue-100 text-blue-800 text-xs px-2.5 py-1 rounded-full font-bold uppercase tracking-wider">Family Care</span>;
      case 'CARETAKER':
        return <span className="bg-purple-100 text-purple-800 text-xs px-2.5 py-1 rounded-full font-bold uppercase tracking-wider">Caretaker</span>;
      default:
        return null;
    }
  };

  return (
    <>
      <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            {/* Logo */}
            <div className="flex items-center gap-6">
              <Link to="/dashboard" className="flex items-center gap-3 group focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-lg p-1">
                <div className="w-11 h-11 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-blue-500/25 group-hover:scale-105 transition-transform">
                  <Heart className="w-6 h-6 fill-white" />
                </div>
                <div>
                  <span className="text-2xl font-black tracking-tight text-slate-900 group-hover:text-blue-600 transition-colors">
                    ElderCare
                  </span>
                  <span className="block text-[10px] uppercase font-bold tracking-widest text-blue-600">Smart Healthcare</span>
                </div>
              </Link>

              {user && (
                <div className="hidden lg:flex items-center gap-2 pl-4 border-l border-slate-200">
                  {getRoleBadge(user.role)}
                </div>
              )}
            </div>

            {/* Profile Selector for Family / Caretaker */}
            {user && user.role !== 'ELDERLY' && user.connected_profiles && user.connected_profiles.length > 0 && (
              <div className="hidden md:flex items-center gap-2 bg-slate-100/80 px-3 py-1.5 rounded-xl border border-slate-200">
                <span className="text-xs font-semibold text-slate-500">Active Senior:</span>
                <select
                  value={activeProfileId || ''}
                  onChange={(e) => setActiveProfileId(e.target.value)}
                  className="bg-transparent text-sm font-bold text-slate-800 focus:outline-none cursor-pointer"
                >
                  {user.connected_profiles.map((p) => (
                    <option key={p.profile_id} value={p.profile_id}>
                      {p.profile_name} ({p.relationship_title})
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Accessibility & Action Buttons */}
            <div className="flex items-center gap-2.5">
              {/* High Contrast Mode Toggle */}
              <button
                type="button"
                onClick={toggleHighContrast}
                title={highContrast ? 'Switch to Normal Contrast' : 'Switch to High Contrast (Senior Accessibility)'}
                className={`p-2.5 rounded-xl font-medium text-xs flex items-center gap-1.5 border transition-all ${
                  highContrast 
                    ? 'bg-black text-white border-black ring-2 ring-blue-500' 
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200 border-slate-200'
                }`}
              >
                <Eye className="w-4 h-4" />
                <span className="hidden sm:inline font-bold">Contrast</span>
              </button>

              {/* Large Font Mode Toggle */}
              <button
                type="button"
                onClick={toggleLargeText}
                title={largeText ? 'Switch to Standard Font Size' : 'Switch to Large Font Size (Senior Accessibility)'}
                className={`p-2.5 rounded-xl font-medium text-xs flex items-center gap-1.5 border transition-all ${
                  largeText 
                    ? 'bg-blue-600 text-white border-blue-600 ring-2 ring-blue-300' 
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200 border-slate-200'
                }`}
              >
                <Type className="w-4 h-4" />
                <span className="hidden sm:inline font-bold">Text Size</span>
              </button>

              {/* Enter Passcode Shortcut */}
              {user && (
                <button
                  type="button"
                  onClick={() => setIsPasscodeOpen(true)}
                  className="p-2.5 bg-blue-50 hover:bg-blue-100 text-blue-700 font-bold text-xs rounded-xl border border-blue-200 flex items-center gap-1.5 transition-all"
                  title="Connect via Invitation Passcode"
                >
                  <KeyRound className="w-4 h-4" />
                  <span className="hidden sm:inline">Join Passcode</span>
                </button>
              )}

              {/* User Dropdown / Logout */}
              {user ? (
                <div className="flex items-center gap-2 pl-2 border-l border-slate-200">
                  <div className="text-right hidden sm:block">
                    <p className="text-sm font-bold text-slate-900 leading-tight">{user.full_name}</p>
                    <p className="text-xs text-slate-500">{user.email}</p>
                  </div>
                  <button
                    onClick={handleLogout}
                    title="Log Out"
                    className="p-2.5 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-xl transition-colors"
                  >
                    <LogOut className="w-5 h-5" />
                  </button>
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <Link
                    to="/login"
                    className="px-4 py-2 text-sm font-semibold text-slate-700 hover:text-blue-600 transition"
                  >
                    Sign In
                  </Link>
                  <Link
                    to="/register"
                    className="px-5 py-2.5 text-sm font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-xl shadow-md shadow-blue-500/20 transition"
                  >
                    Get Started
                  </Link>
                </div>
              )}
            </div>
          </div>

          {/* Navigation Bar for Authenticated Users */}
          {user && (
            <nav className="flex space-x-1 sm:space-x-3 overflow-x-auto py-2 border-t border-slate-100 scrollbar-none">
              {navLinks.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.name}
                    to={item.path}
                    className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold text-sm whitespace-nowrap transition-all ${
                      isActive
                        ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                        : 'text-slate-600 hover:text-blue-600 hover:bg-slate-100'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
            </nav>
          )}
        </div>
      </header>

      <PasscodeModal
        isOpen={isPasscodeOpen}
        onClose={() => setIsPasscodeOpen(false)}
      />
    </>
  );
};
