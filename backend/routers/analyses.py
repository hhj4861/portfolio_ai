from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from .. import models, database
from ..analyzers import risk_calculator, sector_analyzer, ai_analyzer
from ..services import stock_data
from .auth import get_current_user
import uuid

router = APIRouter(
    prefix="/portfolios/{portfolio_id}/analyze",
    tags=["analysis"]
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def run_analysis_task(analysis_id: uuid.UUID, portfolio_id: uuid.UUID):
    db = database.SessionLocal()
    try:
        analysis = db.query(models.Analysis).get(analysis_id)
        if not analysis:
            return

        portfolio = db.query(models.Portfolio).get(portfolio_id)
        if not portfolio:
            analysis.status = "failed"
            analysis.error_message = "Portfolio not found"
            db.commit()
            return
            
        holdings = portfolio.holdings
        
        # 1. Update Prices
        for h in holdings:
            price = stock_data.get_current_price(h.ticker, h.market)
            stock_data.update_holding_calculations(h, price)
        
        # Recalculate portfolio total logic here if needed, or rely on previous
        total_val = sum(h.market_value for h in holdings)
        portfolio.total_value = total_val
        db.commit()

        # 2. Risk Analysis
        risk_metrics = risk_calculator.calculate_risk_metrics(holdings)
        
        # 3. Sector Analysis
        sector_analysis = sector_analyzer.analyze_sector_distribution(holdings)
        
        # 4. AI Analysis
        ai_result = ai_analyzer.ai_analyze_portfolio(portfolio, risk_metrics, sector_analysis)
        
        # 5. Save Results
        analysis.risk_score = risk_metrics['risk_score']
        analysis.risk_level = risk_metrics['risk_level']
        analysis.beta = risk_metrics['beta']
        analysis.sharpe_ratio = risk_metrics['sharpe_ratio']
        analysis.volatility = risk_metrics['volatility']
        analysis.max_drawdown = risk_metrics['max_drawdown']
        
        analysis.ai_summary = ai_result.get('summary')
        analysis.ai_recommendations = ai_result
        analysis.sector_distribution = sector_analysis
        
        analysis.status = "completed"
        db.commit()
        
    except Exception as e:
        print(f"Analysis failed: {e}")
        analysis.status = "failed"
        analysis.error_message = str(e)
        db.commit()
    finally:
        db.close()

@router.post("/", status_code=202)
def start_analysis(
    portfolio_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verify ownership
    portfolio = db.query(models.Portfolio).filter(
        models.Portfolio.id == portfolio_id,
        models.Portfolio.user_id == current_user.id
    ).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # Create Analysis record
    analysis = models.Analysis(
        portfolio_id=portfolio_id,
        user_id=current_user.id,
        status="processing"
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    background_tasks.add_task(run_analysis_task, analysis.id, portfolio_id)
    
    return {"id": str(analysis.id), "status": "processing"}

@router.get("/{analysis_id}") # Note: this path is slightly different from standard REST structure if nested, but useful
def get_analysis(
    analysis_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    analysis = db.query(models.Analysis).filter(
        models.Analysis.id == analysis_id,
        # models.Analysis.user_id == current_user.id # If we added user_id to Analysis model
    ).first()
    
    # Check portfolio ownership via join? or just if we added user_id to analysis
    # I added user_id to Analysis model in models.py earlier, so we can use it.
    if not analysis or analysis.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Analysis not found")
        
    return analysis
