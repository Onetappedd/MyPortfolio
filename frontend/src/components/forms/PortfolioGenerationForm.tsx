import React, { useState } from 'react';
import { Form, Button, Card, Container, Row, Col } from 'react-bootstrap';
import { PortfolioGenerationRequest, portfolioApi } from '../../services/api';
import { useNavigate } from 'react-router-dom';

const PortfolioGenerationForm: React.FC = () => {
  const [formData, setFormData] = useState<PortfolioGenerationRequest>({
    risk_profile: 'moderate',
    name: '',
    investment_amount: 10000,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'investment_amount' ? parseFloat(value) : value,
    }));
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const portfolio = await portfolioApi.generate(formData);
      navigate(`/portfolios/${portfolio.id}`);
    } catch (err) {
      setError('Failed to generate portfolio. Please try again.');
      console.error('Portfolio generation error:', err);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Container className="mt-4">
      <Card>
        <Card.Header as="h4">Generate New Portfolio</Card.Header>
        <Card.Body>
          {error && <div className="alert alert-danger">{error}</div>}
          
          <Form onSubmit={handleSubmit}>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Portfolio Name (Optional)</Form.Label>
                  <Form.Control
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    placeholder="My Investment Portfolio"
                  />
                </Form.Group>
              </Col>
              
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Risk Profile</Form.Label>
                  <Form.Select 
                    name="risk_profile"
                    value={formData.risk_profile}
                    onChange={handleChange}
                  >
                    <option value="conservative">Conservative</option>
                    <option value="moderate">Moderate</option>
                    <option value="aggressive">Aggressive</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
            
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Investment Amount ($)</Form.Label>
                  <Form.Control
                    type="number"
                    name="investment_amount"
                    value={formData.investment_amount}
                    onChange={handleChange}
                    min="1000"
                    step="1000"
                  />
                </Form.Group>
              </Col>
            </Row>
            
            <Button 
              variant="primary" 
              type="submit" 
              disabled={loading}
              className="mt-3"
            >
              {loading ? 'Generating...' : 'Generate Portfolio'}
            </Button>
          </Form>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default PortfolioGenerationForm;