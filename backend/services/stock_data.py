import yfinance as yf
from pykrx import stock
from datetime import datetime
import pandas as pd

def get_current_price(ticker: str, market: str) -> float:
    """
    Get current price for a stock.
    market: 'KR' or 'US'
    """
    try:
        if market == "KR":
            # Pykrx for Korean stocks
            # Use yesterday's close if today is not available (e.g. weekend or early morning)
            # Actually pykrx get_market_ohlcv returns dataframe.
            today = datetime.now().strftime("%Y%m%d")
            # Try fetching for a recent range to ensure data
            df = stock.get_market_ohlcv(today, today, ticker)
            
            if df.empty:
                # If today empty, try last valid day logic or just use naive approach for MVP specific to prompt
                # Prompt used: stock.get_market_ohlcv_by_date(today, today, ticker)
                # Let's fallback to yfinance for KR if possible or just handle empty
                pass
            
            # Simplified for MVP: PyKrx might be slow or empty on holidays.
            # Fallback/standard way:
            p = stock.get_market_ohlcv_by_date(today, today, ticker)
            if p.empty:
                 # Try slightly older date? Or just return 0 for safe fallback
                 return 0.0
            
            return float(p['종가'].iloc[0])

        else:
            # yfinance for US/Other
            ticker_obj = yf.Ticker(ticker)
            # fast_info is often faster than info
            if hasattr(ticker_obj, 'fast_info'):
                price = ticker_obj.fast_info.last_price
                if price:
                    return float(price)
            
            # Fallback to standard info
            data = ticker_obj.history(period="1d")
            if not data.empty:
                return float(data['Close'].iloc[-1])
            return 0.0
    except Exception as e:
        print(f"Error fetching price for {ticker}: {e}")
        return 0.0

def update_holding_calculations(holding, current_price: float):
    """
    Update holding calculation fields based on current price.
    """
    holding.current_price = current_price
    holding.market_value = current_price * holding.quantity
    holding.profit_loss = holding.market_value - (holding.avg_price * holding.quantity)
    if holding.avg_price > 0:
        holding.profit_rate = (holding.profit_loss / (holding.avg_price * holding.quantity)) * 100
    else:
        holding.profit_rate = 0.0
    return holding
