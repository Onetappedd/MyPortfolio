import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert } from 'react-bootstrap';
import { useAuth } from '../../context/AuthContext';
import { portfolioApi, Portfolio } from '../../services/api';
import RiskMetricsCard from '../../components/analysis/RiskMetricsCard';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

// Define API response interface for portfolio comparison
interface ComparisonMetrics {
  name: string;
  risk_profile: string;
  metrics: {
    volatility: number;
    expected_annual_return: number;
    sharpe_ratio: number;
    max_drawdown: number;
    var_95: number;
  };
}

interface ComparisonResponse {
  [portfolioId: string]: ComparisonMetrics;
}

const PortfolioComparison: React.FC = () => {
  const [userPortfolios, setUserPortfolios] = useState<Portfolio[]>([]);
  const [selectedPortfolios, setSelectedPortfolios] = useState<number[]>([]);
  const [comparisonData, setComparisonData] = useState<ComparisonResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const { isLoggedIn } = useAuth();
  
  // Fetch user's portfolios on component mount
  useEffect(() => {
    const fetchPortfolios = async () => {
      try {
        if (!isLoggedIn) return;
        
        const portfolios = await portfolioApi.getAll();
        setUserPortfolios(portfolios);
      } catch (err) {
        console.error('Error fetching portfolios:', err);
        setError('Failed to load your portfolios');
      }
    };
    
    fetchPortfolios();
  }, [isLoggedIn]);
  
  // Toggle portfolio selection
  const togglePortfolioSelection = (portfolioId: number) => {
    setSelectedPortfolios(prev => {
      if (prev.includes(portfolioId)) {
        return prev.filter(id => id !== portfolioId);
      } else {
        return [...prev, portfolioId];
      }
    });
  };
  
  // Compare selected portfolios
  const comparePortfolios = async () => {
    if (selectedPortfolios.length < 2) {
      setError