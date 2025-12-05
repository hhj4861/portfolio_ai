from typing import List, Dict, Any
from ..models import Holding

SECTOR_MAPPING = {
    # Demo mapping
    '005930': 'IT', '000660': 'IT', 'AAPL': 'IT', 'MSFT': 'IT',
    '035420': '커뮤니케이션', 'GOOGL': '커뮤니케이션',
    '005380': '경기소비재', 'TSLA': '경기소비재',
    '005935': 'IT',
    '068270': '헬스케어', 'JNJ': '헬스케어',
    '051910': '소재',
    '006400': '소재',
    '005490': '소재', # POSCO
    '105560': '금융', # KB Financial
}

# Korean Sector Names
IDEAL_WEIGHTS = {
    'IT': 0.25,
    '금융': 0.20,
    '헬스케어': 0.15,
    '경기소비재': 0.15,
    '산업재': 0.10,
    '에너지': 0.10,
    '기타': 0.05,
    '커뮤니케이션': 0.0, # Just to handle if present
    '소재': 0.0
}

def analyze_sector_distribution(holdings: List[Holding]) -> Dict[str, Any]:
    current_dist = {}
    total_val = sum(h.market_value for h in holdings)
    
    if total_val == 0:
        return {'current': {}, 'ideal': IDEAL_WEIGHTS, 'issues': []}

    for h in holdings:
        # Try to get sector from mapping, otherwise from holding data if available, else Other
        raw_sector = SECTOR_MAPPING.get(h.ticker, h.sector or 'Other')
        # Map some common english if they come from h.sector
        sector_map = {
            'Finance': '금융', 'Healthcare': '헬스케어', 'Consumer': '경기소비재',
            'Industrial': '산업재', 'Energy': '에너지', 'Communication': '커뮤니케이션',
            'Materials': '소재', 'IT': 'IT', 'Other': '기타'
        }
        sector = sector_map.get(raw_sector, raw_sector)
        if sector not in sector_map.values() and sector != 'IT':
             sector = '기타'

        weight = h.market_value / total_val
        current_dist[sector] = current_dist.get(sector, 0) + weight

    issues = []
    # Only check major ideal sectors
    check_sectors = ['IT', '금융', '헬스케어', '경기소비재', '산업재', '에너지']
    
    for sector in check_sectors:
        ideal = IDEAL_WEIGHTS.get(sector, 0.0)
        curr = current_dist.get(sector, 0.0)
        diff = curr - ideal
        
        if abs(diff) > 0.10:
            issues.append({
                'sector': sector,
                'current': float(curr),
                'recommended': float(ideal),
                'diff': float(diff),
                'action': 'reduce' if diff > 0 else 'increase'
            })
            
    return {
        'current': current_dist,
        'ideal': IDEAL_WEIGHTS,
        'issues': issues
    }
