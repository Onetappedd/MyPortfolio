import axios, { AxiosResponse } from 'axios';

// Base API configuration
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Allocation {
  id?: number;
  asset_class: string;
  asset_name: string;
  allocation_percentage: number;
  ticker?: string;
  sector?: string;
  region?: string;
  metadata?: Record<string, any>;
}

export interface Portfolio {
  id?: number;
  name: string;
  risk_profile: string;
  created_at?: string;
  updated_at?: string;
  allocations: Allocation[];
}

export interface PortfolioGenerationRequest {
  risk_profile: 'conservative' | 'moderate' | 'aggressive';
  investment_amount?: number;
  constraints?: Record<string, any>;
  name?: string;
}

// Portfolio API methods
export const portfolioApi = {
  // Get all portfolios
  getAll: async (): Promise<Portfolio[]> => {
    const response: AxiosResponse<Portfolio[]> = await api.get('/portfolios');
    return response.data;
  },
  
  // Get portfolio by ID
  getById: async (id: number): Promise<Portfolio> => {
    const response: AxiosResponse<Portfolio> = await api.get(`/portfolios/${id}`);
    return response.data;
  },
  
  // Generate portfolio
  generate: async (request: PortfolioGenerationRequest): Promise<Portfolio> => {
    const response: AxiosResponse<Portfolio> = await api.post('/portfolios/generate', request);
    return response.data;
  },
  
  // Update portfolio
  update: async (id: number, portfolio: Partial<Portfolio>): Promise<Portfolio> => {
    const response: AxiosResponse<Portfolio> = await api.put(`/portfolios/${id}`, portfolio);
    return response.data;
  },
  
  // Delete portfolio
  delete: async (id: number): Promise<void> => {
    await api.delete(`/portfolios/${id}`);
  },
};

export default api;