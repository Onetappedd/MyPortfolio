import React from 'react';
import { Card, Table, Badge } from 'react-bootstrap';

interface RiskMetrics {
  volatility: number;
  expected_annual_return: number;
  sharpe_ratio: number;
  max_drawdown: number;
  var_95: number;
}

interface RiskMetricsCardProps {
  metrics: RiskMetrics;
  title?: string;
}

const RiskMetricsCard: React.FC<RiskMetricsCardProps> = ({ metrics, title = "Risk Metrics" }) => {
  // Helper function to format percentages
  const formatPercent = (value: number): string => {
    return `${(value * 100).toFixed(2)}%`;
  };
  
  // Helper to determine risk level based on volatility
  const getRiskLevel = (volatility: number): { text: string; color: string } => {
    if (volatility < 0.1) {
      return { text: "Low", color: "success" };
    } else if (volatility < 0.2) {
      return { text: "Moderate", color: "primary" };
    } else if (volatility < 0.3) {
      return { text: "High", color: "warning" };
    } else {
      return { text: "Very High", color: "danger" };
    }
  };
  
  // Helper to interpret Sharpe ratio
  const getSharpeRating = (ratio: number): { text: string; color: string } => {
    if (ratio < 0) {
      return { text: "Poor", color: "danger" };
    } else if (ratio < 1) {
      return { text: "Below Average", color: "warning" };
    } else if (ratio < 2) {
      return { text: "Good", color: "primary" };
    } else {
      return { text: "Excellent", color: "success" };
    }
  };
  
  const riskLevel = getRiskLevel(metrics.volatility);
  const sharpeRating = getSharpeRating(metrics.sharpe_ratio);
  
  return (
    <Card className="mb-4">
      <Card.Header>
        <h5 className="mb-0">{title}</h5>
      </Card.Header>
      <Card.Body>
        <Table borderless>
          <tbody>
            <tr>
              <td><strong>Expected Annual Return:</strong></td>
              <td>{formatPercent(metrics.expected_annual_return)}</td>
            </tr>
            <tr>
              <td>
                <strong>Risk Level:</strong>
              </td>
              <td>
                <Badge bg={riskLevel.color}>{riskLevel.text}</Badge>
                <span className="ms-2">(Volatility: {formatPercent(metrics.volatility)})</span>
              </td>
            </tr>
            <tr>
              <td>
                <strong>Sharpe Ratio:</strong>
                <div className="text-muted small">Risk-adjusted return</div>
              </td>
              <td>
                <Badge bg={sharpeRating.color}>{sharpeRating.text}</Badge>
                <span className="ms-2">({metrics.sharpe_ratio.toFixed(2)})</span>
              </td>
            </tr>
            <tr>
              <td>
                <strong>Maximum Drawdown:</strong>
                <div className="text-muted small">Largest historical loss</div>
              </td>
              <td>{formatPercent(metrics.max_drawdown)}</td>
            </tr>
            <tr>
              <td>
                <strong>Value at Risk (95%):</strong>
                <div className="text-muted small">Potential daily loss</div>
              </td>
              <td>{formatPercent(Math.abs(metrics.var_95))}</td>
            </tr>
          </tbody>
        </Table>
      </Card.Body>
    </Card>
  );
};

export default RiskMetricsCard;