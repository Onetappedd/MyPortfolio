from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import portfolios, users
from .db.session import engine
from .db.base import Base

# Create all tables in database
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Portfolio Management API",
    description="API for generating and managing investment portfolios",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(portfolios.router, prefix="/api/portfolios", tags=["portfolios"])
app.include_router(users.router, prefix="/api/users", tags=["users"])

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Portfolio Management API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }