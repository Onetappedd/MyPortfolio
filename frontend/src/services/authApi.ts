import api from './api';
import { AxiosResponse } from 'axios';

export interface LoginRequest {
  username: string;  // Using username for OAuth2 compatibility
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: number;
  email: string;
  full_name?: string;
  is_active: boolean;
}

const TOKEN_KEY = 'portfolio_auth_token';

// Auth service methods
export const authApi = {
  // Login user
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const formData = new FormData();
    formData.append('username', data.username);
    formData.append('password', data.password);
    
    const response: AxiosResponse<AuthResponse> = await api.post(
      '/auth/login',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    
    // Store token in localStorage
    localStorage.setItem(TOKEN_KEY, response.data.access_token);
    
    // Add token to axios default headers
    api.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`;
    
    return response.data;
  },
  
  // Register user
  register: async (data: RegisterRequest): Promise<User> => {
    const response: AxiosResponse<User> = await api.post('/auth/register', data);
    return response.data;
  },
  
  // Get current user
  getCurrentUser: async (): Promise<User> => {
    const response: AxiosResponse<User> = await api.get('/users/me');
    return response.data;
  },
  
  // Check if user is logged in
  isLoggedIn: (): boolean => {
    return !!localStorage.getItem(TOKEN_KEY);
  },
  
  // Logout user
  logout: (): void => {
    localStorage.removeItem(TOKEN_KEY);
    delete api.defaults.headers.common['Authorization'];
  },
  
  // Initialize auth state (called on app start)
  initAuth: (): void => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
  },
};

export default authApi;