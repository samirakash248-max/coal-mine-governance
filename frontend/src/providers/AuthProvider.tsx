import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { apiClient } from '../api/client';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  permissions: string[];
  mine_id?: string;
}

interface AuthContextType {
  token: string | null;
  user: User | null;
  login: (token: string) => void;
  logout: () => void;
  isAuthenticated: boolean;
  isLoading: boolean;
  hasPermission: (perm: string) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('access_token'));
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchUser = useCallback(async () => {
    if (!token) {
      setUser(null);
      setIsLoading(false);
      return;
    }
    
    try {
      // In the frontend API client interceptor, 401s usually trigger token removal.
      const res = await apiClient.get<User>('/api/v1/auth/me');
      setUser(res.data);
      localStorage.setItem('access_token', token);
    } catch (err) {
      console.error("Failed to fetch user:", err);
      // Let the interceptor handle the logout if it's a 401
      if ((err as any)?.response?.status === 401 || (err as any)?.response?.status === 403) {
        logout();
      }
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  const login = (newToken: string) => {
    setToken(newToken);
    localStorage.setItem('access_token', newToken);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('access_token');
    
    // Optional backend logout
    apiClient.post('/api/v1/auth/logout').catch(() => {});
  };

  const hasPermission = useCallback((perm: string) => {
    if (!user) return false;
    if (user.role === 'system_admin' || user.role === 'admin') return true;
    return user.permissions.includes(perm);
  }, [user]);

  return (
    <AuthContext.Provider value={{ token, user, login, logout, isAuthenticated: !!user, isLoading, hasPermission }}>
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
