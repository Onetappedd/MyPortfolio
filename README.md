# Portfolio Management Application

A comprehensive portfolio management system that allows users to generate, save, and analyze investment portfolios based on their risk preferences.

## Features

- Generate custom portfolios based on risk profiles (conservative, moderate, aggressive)
- Visualize asset allocations with interactive charts
- Save and manage multiple portfolios
- Compare portfolio allocations
- Dockerized for easy setup and deployment

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)

### Running the Application

1. Clone this repository
   ```bash
   git clone https://github.com/yourusername/portfolio-management-app.git
   cd portfolio-management-app
   ```

2. Start the application with the provided script
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

3. Access the application:
   - Frontend: http://localhost:3000
   - API Documentation: http://localhost:8000/docs

### Manual Setup

If you prefer to run the services separately:

1. Start the database
   ```bash
   docker-compose up -d postgres
   ```

2. Start the backend
   ```bash
   docker-compose up -d backend
   ```

3. Start the frontend
   ```bash
   docker-compose up -d frontend
   ```

## Development Setup

### Backend (FastAPI)

1. Set up a virtual environment
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Set environment variables
   ```bash
   export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/portfolio_management
   ```

4. Run the development server
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend (React)

1. Install dependencies
   ```bash
   cd frontend
   npm install
   ```

2. Set environment variables
   ```
   # Create .env file
   REACT_APP_API_BASE_URL=http://localhost:8000/api
   ```

3. Start development server
   ```bash
   npm start
   ```

## Project Structure

```
portfolio-app/
├── backend/             # FastAPI backend
├── frontend/            # React frontend
├── docker-compose.yml   # Docker Compose configuration
└── start.sh             # One-click startup script
```

## Technologies Used

- **Backend**: FastAPI, PostgreSQL, SQLAlchemy, Alembic
- **Frontend**: React, TypeScript, Chart.js, React Bootstrap
- **DevOps**: Docker, Docker Compose, GitHub Actions

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.