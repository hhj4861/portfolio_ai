from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database
from .auth import get_current_user
import uuid

router = APIRouter(
    prefix="/portfolios",
    tags=["portfolios"]
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.Portfolio)
def create_portfolio(
    portfolio: schemas.PortfolioCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_portfolio = models.Portfolio(
        name=portfolio.name,
        description=portfolio.description,
        user_id=current_user.id
    )
    db.add(db_portfolio)
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio

@router.get("/", response_model=List[schemas.Portfolio])
def read_portfolios(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    portfolios = db.query(models.Portfolio).filter(
        models.Portfolio.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return portfolios

@router.get("/{portfolio_id}", response_model=schemas.Portfolio)
def read_portfolio(
    portfolio_id: uuid.UUID, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    portfolio = db.query(models.Portfolio).filter(
        models.Portfolio.id == portfolio_id,
        models.Portfolio.user_id == current_user.id
    ).first()
    if portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio

@router.delete("/{portfolio_id}")
def delete_portfolio(
    portfolio_id: uuid.UUID, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    portfolio = db.query(models.Portfolio).filter(
        models.Portfolio.id == portfolio_id,
        models.Portfolio.user_id == current_user.id
    ).first()
    if portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    db.delete(portfolio)
    db.commit()
    return {"ok": True}
