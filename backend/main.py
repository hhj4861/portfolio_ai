from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, portfolios, holdings, analyses
from .config import settings

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="PortfolioAI API")

# CORS setup
origins = [
    settings.FRONTEND_URL,
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(portfolios.router, prefix="/api")
app.include_router(holdings.router, prefix="/api")
app.include_router(analyses.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to PortfolioAI API"}
