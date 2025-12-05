from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255))
    full_name = Column(String(100))
    investment_goal = Column(String(50))  # 'growth', 'stability', 'retirement'
    risk_tolerance = Column(String(50))   # 'safe', 'moderate', 'aggressive'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    portfolios = relationship("Portfolio", back_populates="user")

class Portfolio(Base):
    __tablename__ = "portfolios"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    total_value = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    profit_loss = Column(Float, default=0.0)
    profit_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="portfolios")
    holdings = relationship("Holding", back_populates="portfolio")
    analyses = relationship("Analysis", back_populates="portfolio")

class Holding(Base):
    __tablename__ = "holdings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id"))
    ticker = Column(String(20), nullable=False)
    name = Column(String(100))
    market = Column(String(10))  # 'US', 'KR'
    sector = Column(String(50))
    quantity = Column(Integer, nullable=False)
    avg_price = Column(Float, nullable=False)
    current_price = Column(Float, default=0.0)
    market_value = Column(Float, default=0.0)
    profit_loss = Column(Float, default=0.0)
    profit_rate = Column(Float, default=0.0)
    weight = Column(Float, default=0.0)  # Portfolio weight
    created_at = Column(DateTime, default=datetime.utcnow)
    
    portfolio = relationship("Portfolio", back_populates="holdings")

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id")) # Add user_id as per prompt logic
    status = Column(String(50), default="pending") # processing, completed, failed
    
    risk_score = Column(Integer)  # 1-10
    risk_level = Column(String(50))
    beta = Column(Float)
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)
    volatility = Column(Float)
    
    ai_summary = Column(Text)
    ai_recommendations = Column(JSONB)
    sector_distribution = Column(JSONB)
    optimization_result = Column(JSONB)
    error_message = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    portfolio = relationship("Portfolio", back_populates="analyses")
