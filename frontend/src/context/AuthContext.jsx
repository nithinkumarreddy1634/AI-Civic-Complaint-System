import React, { createContext, useState, useEffect, useCallback } from 'react';
import authService from '../services/authService';

export const AuthContext = createContext();

const ROLE_ACCOUNTS = {
  citizen: { email: 'citizen@example.com', password: 'password123' },
  admin: { email: 'admin@civicai.com', password: 'admin123' },
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [activeRole, setActiveRole] = useState(localStorage.getItem('civic_role') || 'citizen');
  const [loading, setLoading] = useState(true);

  // Auto-login helper for seamless password-free operation
  const autoLoginRole = useCallback(async (roleToUse = 'citizen') => {
    const creds = ROLE_ACCOUNTS[roleToUse] || ROLE_ACCOUNTS.citizen;
    try {
      const data = await authService.login(creds.email, creds.password);
      if (data?.access_token) {
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('civic_role', roleToUse);
        setToken(data.access_token);
        let userData = data.user;
        if (!userData) {
          userData = await authService.getProfile();
        }
        setUser(userData);
        setActiveRole(roleToUse);
        return userData;
      }
    } catch (err) {
      console.warn(`Silent login for ${roleToUse} failed:`, err);
    }
    return null;
  }, []);

  useEffect(() => {
    const initSession = async () => {
      const savedRole = localStorage.getItem('civic_role') || 'citizen';
      if (token) {
        try {
          const profile = await authService.getProfile();
          if (profile) {
            setUser(profile);
            setActiveRole(profile.role || savedRole);
            setLoading(false);
            return;
          }
        } catch (e) {
          console.warn('Token expired or invalid, refreshing automatically...', e);
        }
      }
      // If no valid token, auto-login into the active role seamlessly
      await autoLoginRole(savedRole);
      setLoading(false);
    };

    initSession();
  }, [autoLoginRole, token]);

  const switchRole = async (targetRole) => {
    setLoading(true);
    const validRole = targetRole === 'admin' ? 'admin' : 'citizen';
    const profile = await autoLoginRole(validRole);
    setLoading(false);
    return profile;
  };

  const login = async (email, password) => {
    const data = await authService.login(email, password);
    localStorage.setItem('token', data.access_token);
    setToken(data.access_token);
    let userData = data.user;
    if (!userData) {
      userData = await authService.getProfile();
    }
    setUser(userData);
    if (userData?.role) {
      setActiveRole(userData.role);
      localStorage.setItem('civic_role', userData.role);
    }
    return { ...data, user: userData };
  };

  const register = async (name, email, password) => {
    return await authService.register(name, email, password);
  };

  const logout = () => {
    // In zero-auth-page mode, logout resets to citizen mode
    switchRole('citizen');
  };

  const value = {
    user,
    token,
    loading,
    activeRole: user?.role || activeRole,
    switchRole,
    login,
    register,
    logout,
    isAdmin: user?.role === 'admin',
    isCitizen: user?.role === 'citizen' || !user || user?.role !== 'admin',
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;
