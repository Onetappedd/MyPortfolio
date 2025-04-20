import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Row, Col, Card, Table, Button, Alert, Spinner } from 'react-bootstrap';
import { Portfolio, portfolioApi } from '../../services/api';
import PortfolioAllocationChart from '../../components/charts/PortfolioAllocationChart';

const PortfolioDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  
  useEffect(() => {
    const fetchPortfolio = async () => {
      try {
        if (!id) throw new Error('Portfolio ID is missing');
        const data = await portfolioApi.getById(parseInt(id));
        setPortfolio(data);
      } catch (err) {
        setError('Failed to load portfolio data');
        console.error('Error fetching portfolio:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchPortfolio();
  }, [id]);
  
  const handleDelete = async () => {
    if (!id || !window.confirm('Are you sure you want to delete this portfolio?')) return;
    
    try {
      await portfolioApi.delete(parseInt(id));
      navigate('/portfolios');
    } catch (err) {
      setError('Failed to delete portfolio');
      console.error('Error deleting portfolio:', err);
    }
  };
  
  if (loading) {
    return (
      <Container className="text-center mt-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
      </Container>
    );
  }
  
  if (error || !portfolio) {
    return (
      <Container className="mt-5">
        <Alert variant="danger">
          {error || 'Portfolio not found'}
        </Alert>
      </Container>
    );
  }
  
  // Calculate total allocation to verify it equals 100%
  const totalAllocation = portfolio.allocations.reduce(
    (sum, allocation) => sum + allocation.allocation_percentage, 
    0
  );
  
  return (
    <Container className="mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>{portfolio.name}</h2>
        <div>
          <Button 
            variant="outline-primary" 
            className="me-2" 
            onClick={() => navigate(`/portfolios/edit/${id}`)}
          >
            Edit Portfolio
          </Button>
          <Button variant="danger" onClick={handleDelete}>
            Delete Portfolio
          </Button>
        </div>
      </div>
      
      <Row>
        <Col lg={4} md={6} className="mb-4">
          <Card>
            <Card.Header>Portfolio Details</Card.Header>
            <Card.Body>
              <Table borderless>
                <tbody>
                  <tr>
                    <td><strong>Risk Profile:</strong></td>
                    <td>{portfolio.risk_profile}</td>
                  </tr>
                  <tr>
                    <td><strong>Created:</strong></td>
                    <td>{new Date(portfolio.created_at || '').toLocaleDateString()}</td>
                  </tr>
                  <tr>
                    <td><strong>Last Updated:</strong></td>
                    <td>
                      {portfolio.updated_at ? 
                        new Date(portfolio.updated_at).toLocaleDateString() : 
                        'Not modified'}
                    </td>
                  </tr>
                  <tr>
                    <td><strong>Total Allocation:</strong></td>
                    <td>{(totalAllocation * 100).toFixed(2)}%</td>
                  </tr>
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Col>
        
        <Col lg={8} md={6} className="mb-4">
          <PortfolioAllocationChart allocations={portfolio.allocations} />
        </Col>
      </Row>
      
      <Card>
        <Card.Header>Allocation Details</Card.Header>
        <Card.Body>
          <Table striped hover responsive>
            <thead>
              <tr>
                <th>Asset Class</th>
                <th>Asset Name</th>
                <th>Allocation</th>
                <th>Ticker</th>
                <th>Sector</th>
                <th>Region</th>
              </tr>
            </thead>
            <tbody>
              {portfolio.allocations.map((allocation) => (
                <tr key={allocation.id || allocation.asset_name}>
                  <td>{allocation.asset_class}</td>
                  <td>{allocation.asset_name}</td>
                  <td>{(allocation.allocation_percentage * 100).toFixed(2)}%</td>
                  <td>{allocation.ticker || '-'}</td>
                  <td>{allocation.sector || '-'}</td>
                  <td>{allocation.region || '-'}</td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default PortfolioDetail;