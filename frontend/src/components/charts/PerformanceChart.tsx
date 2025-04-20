import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  Title, 
  Tooltip, 
  Legend,
  TimeScale 
} from 'chart.js';
import 'chartjs-adapter-date-fns';
import { Card, Form, Row, Col } from 'react-bootstrap';
import { PortfolioSnapshot } from '../../services/api';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
);

interface PerformanceChartProps {
  portfolioId: number;
  history: PortfolioSnapshot[];
  interval: 'daily' | 'weekly' | 'monthly';
  onIntervalChange: (interval: 'daily' | 'weekly' | 'monthly') => void;
  isLoading: boolean;
}

const PerformanceChart: React.FC<PerformanceChartProps> = ({
  portfolioId,
  history,
  interval,
  onIntervalChange,
  isLoading,
}) => {
  // Format data for chart
  const chartData = {
    datasets: [
      {
        label: 'Portfolio Value',
        data: history.map(snapshot => ({
          x: new Date(snapshot.date),
          y: snapshot.total_value,
        })),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        tension: 0.1,
      },
    ],
  };
  
  // Chart options
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            const label = context.dataset.label || '';
            const value = context.raw.y || 0;
            return `${label}: $${value.toFixed(2)}`;
          }
        }
      }
    },
    scales: {
      x: {
        type: 'time' as const,
        time: {
          unit: interval === 'daily' ? 'day' : 
                interval === 'weekly' ? 'week' : 'month',
        },
        title: {
          display: true,
          text: 'Date',
        },
      },
      y: {
        title: {
          display: true,
          text: 'Value ($)',
        },
        min: function(context: any) {
          const min = Math.min(...history.map(s => s.total_value));
          return Math.max(0, min * 0.9); // 90% of minimum, but never below zero
        },
      },
    },
  };
  
  const handleIntervalChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onIntervalChange(e.target.value as 'daily' | 'weekly' | 'monthly');
  };
  
  return (
    <Card>
      <Card.Header className="d-flex justify-content-between align-items-center">
        <div>Portfolio Performance</div>
        <Form.Select 
          className="w-auto" 
          value={interval} 
          onChange={handleIntervalChange}
          disabled={isLoading}
        >
          <option value="daily">Daily</option>
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
        </Form.Select>
      </Card.Header>
      <Card.Body>
        {isLoading ? (
          <div className="text-center p-5">Loading performance data...</div>
        ) : history.length > 0 ? (
          <div style={{ height: '400px' }}>
            <Line data={chartData} options={chartOptions} />
          </div>
        ) : (
          <div className="text-center p-5">
            No performance history available yet. Create a snapshot to track performance.
          </div>
        )}
      </Card.Body>
    </Card>
  );
};

export default PerformanceChart;