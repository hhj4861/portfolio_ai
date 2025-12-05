from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# User Schemas
class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Holding Schemas
class HoldingBase(BaseModel):
    ticker: str
    name: Optional[str] = None
    market: str
    quantity: int
    avg_price: float

class HoldingCreate(HoldingBase):
    pass

class Holding(HoldingBase):
    id: UUID
    portfolio_id: UUID
    current_price: float
    market_value: float
    profit_loss: float
    profit_rate: float
    weight: float

    class Config:
        from_attributes = True

# Portfolio Schemas
class PortfolioBase(BaseModel):
    name: str
    description: Optional[str] = None

class PortfolioCreate(PortfolioBase):
    pass

class Portfolio(PortfolioBase):
    id: UUID
    total_value: float
    profit_rate: float
    holdings: List[Holding] = []

    class Config:
        from_attributes = True

# Analysis Schema
class VideoAnalysisCreate(BaseModel):
    pass # Analysis creation trigger usually doesn't need body, just portfolio ID path param
