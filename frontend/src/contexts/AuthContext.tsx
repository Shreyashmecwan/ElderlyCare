import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from '../types';
import { authService } from '../services/authService';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  activeProfileId: string | null;
  setActiveProfileId: (id: string | null) => void;
  login: (email: string, pass: string) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('eldercare_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('eldercare_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [activeProfileId, setActiveProfileId] = useState<string | null>(() => {
    return localStorage.getItem('eldercare_active_profile_id') || null;
  });

  useEffect(() => {
    if (activeProfileId) {
      localStorage.setItem('eldercare_active_profile_id', activeProfileId);
    } else {
      localStorage.removeItem('eldercare_active_profile_id');
    }
  }, [activeProfileId]);

  const refreshUser = async () => {
    try {
      if (token) {
        const res = await authService.getMe();
        if (res.success) {
          setUser(res.data);
          localStorage.setItem('eldercare_user', JSON.stringify(res.data));
          // If elderly user has profile, default active profile
          if (res.data.role === 'ELDERLY' && res.data.profile_id) {
            setActiveProfileId(res.data.profile_id);
          } else if (res.data.connected_profiles && res.data.connected_profiles.length > 0 && !activeProfileId) {
            setActiveProfileId(res.data.connected_profiles[0].profile_id);
          }
        }
      }
    } catch (e) {
      console.error("Failed to refresh user:", e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      refreshUser();
    } else {
      setIsLoading(false);
    }
  }, [token]);

  const login = async (email: string, pass: string) => {
    const res = await authService.login({ email, password: pass });
    if (res.success) {
      setToken(res.data.access_token);
      setUser(res.data.user);
      localStorage.setItem('eldercare_token', res.data.access_token);
      localStorage.setItem('eldercare_refresh_token', res.data.refresh_token);
      localStorage.setItem('eldercare_user', JSON.stringify(res.data.user));

      if (res.data.user.role === 'ELDERLY' && res.data.user.profile_id) {
        setActiveProfileId(res.data.user.profile_id);
      }
    } else {
      throw new Error(res.error?.message || 'Login failed');
    }
  };

  const register = async (data: any) => {
    const res = await authService.register(data);
    if (res.success) {
      setToken(res.data.access_token);
      setUser(res.data.user);
      localStorage.setItem('eldercare_token', res.data.access_token);
      localStorage.setItem('eldercare_refresh_token', res.data.refresh_token);
      localStorage.setItem('eldercare_user', JSON.stringify(res.data.user));

      if (res.data.user.profile_id) {
        setActiveProfileId(res.data.user.profile_id);
      }
    } else {
      throw new Error(res.error?.message || 'Registration failed');
    }
  };

  const logout = () => {
    authService.logout();
    setUser(null);
    setToken(null);
    setActiveProfileId(null);
    localStorage.removeItem('eldercare_active_profile_id');
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, activeProfileId, setActiveProfileId, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
