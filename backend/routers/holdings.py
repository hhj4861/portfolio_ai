from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database
from ..services import stock_data
from .auth import get_current_user
import uuid

router = APIRouter(
    prefix="/portfolios/{portfolio_id}/holdings",
    tags=["holdings"]
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_portfolio_owner(portfolio_id: uuid.UUID, user_id: uuid.UUID, db: Session):
    portfolio = db.query(models.Portfolio).filter(
        models.Portfolio.id == portfolio_id,
        models.Portfolio.user_id == user_id
    ).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio

@router.post("/", response_model=schemas.Holding)
def create_holding(
    portfolio_id: uuid.UUID,
    holding: schemas.HoldingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    portfolio = verify_portfolio_owner(portfolio_id, current_user.id, db)
    
    # Fetch current price
    current_price = stock_data.get_current_price(holding.ticker, holding.market)
    
    db_holding = models.Holding(
        portfolio_id=portfolio_id,
        ticker=holding.ticker,
        name=holding.name,
        market=holding.market,
        quantity=holding.quantity,
        avg_price=holding.avg_price
    )
    
    # Update calculations
    stock_data.update_holding_calculations(db_holding, current_price)
    
    db.add(db_holding)
    db.commit()
    db.refresh(db_holding)
    
    # Recalculate Portfolio Totals
    # Ideally should be a separate service or trigger, but inline for MVP
    update_portfolio_totals(portfolio, db)
    
    return db_holding

@router.get("/", response_model=List[schemas.Holding])
def read_holdings(
    portfolio_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    verify_portfolio_owner(portfolio_id, current_user.id, db)
    holdings = db.query(models.Holding).filter(models.Holding.portfolio_id == portfolio_id).all()
    return holdings

def update_portfolio_totals(portfolio: models.Portfolio, db: Session):
    holdings = db.query(models.Holding).filter(models.Holding.portfolio_id == portfolio.id).all()
    
    total_val = sum(h.market_value for h in holdings)
    total_cost = sum(h.avg_price * h.quantity for h in holdings)
    
    portfolio.total_value = total_val
    portfolio.total_cost = total_cost
    portfolio.profit_loss = total_val - total_cost
    if total_cost > 0:
        portfolio.profit_rate = (portfolio.profit_loss / total_cost) * 100
    else:
        portfolio.profit_rate = 0.0
        
    # Update weights
    if total_val > 0:
        for h in holdings:
            h.weight = (h.market_value / total_val) * 100
    
    db.commit()
