import React, { createContext, useContext, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import authApi, { User, LoginRequest, RegisterRequest } from '../services/authApi';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isLoggedIn: boolean;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>(null!);

export const useAuth = () => useContext(AuthContext);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const navigate = useNavigate();
  
  useEffect(() => {
    // Initialize authentication on app load
    const initAuth = async () => {
      setIsLoading(true);
      try {
        if (authApi.isLoggedIn()) {
          authApi.initAuth();
          const currentUser = await authApi.getCurrentUser();
          setUser(currentUser);
        }
      } catch (error) {
        console.error('Authentication initialization failed:', error);
        authApi.logout();
      } finally {
        setIsLoading(false);
      }
    };
    
    initAuth();
  }, []);
  
  const login = async (data: LoginRequest) => {
    setIsLoading(true);
    try {
      await authApi.login(data);
      const currentUser = await authApi.getCurrentUser();
      setUser(currentUser);
      navigate('/portfolios');
    } finally {
      setIsLoading(false);
    }
  };
  
  const register = async (data: RegisterRequest) => {
    setIsLoading(true);
    try {
      await authApi.register(data);
      await login({ username: data.email, password: data.password });
    } finally {
      setIsLoading(false);
    }
  };
  
  const logout = () => {
    authApi.logout();
    setUser(null);
    navigate('/login');
  };
  
  const value = {
    user,
    isLoading,
    isLoggedIn: !!user,
    login,
    register,
    logout
  };
  
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};