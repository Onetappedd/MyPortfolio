import React from 'react';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Card, Container, Row, Col } from 'react-bootstrap';
import { Allocation } from '../../services/api';

// Register ChartJS components
ChartJS.register(ArcElement, Tooltip, Legend);

interface PortfolioAllocationChartProps {
  allocations: Allocation[];
}

// Generate random colors for chart segments
const generateColors = (count: number): string[] => {
  const colors: string[] = [];
  for (let i = 0; i < count; i++) {
    const hue = (i * 137.5) % 360; // Golden angle approximation for good distribution
    colors.push(`hsl(${hue}, 70%, 60%)`);
  }
  return colors;
};

const PortfolioAllocationChart: React.FC<PortfolioAllocationChartProps> = ({ allocations }) => {
  // Group allocations by asset class
  const assetClassData = allocations.reduce<Record<string, number>>((acc, allocation) => {
    const { asset_class, allocation_percentage } = allocation;
    acc[asset_class] = (acc[asset_class] || 0) + allocation_percentage;
    return acc;
  }, {});
  
  // Prepare data for asset class chart
  const assetClassLabels = Object.keys(assetClassData);
  const assetClassValues = Object.values(assetClassData);
  const assetClassColors = generateColors(assetClassLabels.length);
  
  // Prepare data for specific assets chart
  const assetLabels = allocations.map(a => a.asset_name);
  const assetValues = allocations.map(a => a.allocation_percentage);
  const assetColors = generateColors(allocations.length);
  
  const assetClassChartData = {
    labels: assetClassLabels,
    datasets: [
      {
        data: assetClassValues,
        backgroundColor: assetClassColors,
        borderColor: assetClassColors.map(c => c.replace('60%', '50%')),
        borderWidth: 1,
      },
    ],
  };
  
  const assetsChartData = {
    labels: assetLabels,
    datasets: [
      {
        data: assetValues,
        backgroundColor: assetColors,
        borderColor: assetColors.map(c => c.replace('60%', '50%')),
        borderWidth: 1,
      },
    ],
  };
  
  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom' as const,
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            const label = context.label || '';
            const value = context.raw || 0;
            return `${label}: ${(value * 100).toFixed(2)}%`;
          }
        }
      }
    },
  };
  
  return (
    <Container>
      <Row>
        <Col lg={6}>
          <Card className="mb-4">
            <Card.Header>Allocation by Asset Class</Card.Header>
            <Card.Body>
              <div style={{ height: '300px' }}>
                <Pie data={assetClassChartData} options={chartOptions} />
              </div>
            </Card.Body>
          </Card>
        </Col>
        
        <Col lg={6}>
          <Card className="mb-4">
            <Card.Header>Allocation by Specific Assets</Card.Header>
            <Card.Body>
              <div style={{ height: '300px' }}>
                <Pie data={assetsChartData} options={chartOptions} />
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default PortfolioAllocationChart;