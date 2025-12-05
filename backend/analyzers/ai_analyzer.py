from openai import OpenAI
from ..config import settings
import json
from ..models import Portfolio

def ai_analyze_portfolio(portfolio: Portfolio, risk_metrics: dict, sector_analysis: dict):
    if not settings.OPENAI_API_KEY or "placeholder" in settings.OPENAI_API_KEY:
        # Return mock response if no key
        return {
            "summary": "AI API 키가 설정되지 않아 데모 분석 결과를 표시합니다. 포트폴리오는 전반적으로 안정적이나 IT 섹터 비중이 높습니다.",
            "strengths": ["높은 수익률 잠재력", "우량주 위주 구성"],
            "weaknesses": ["섹터 분산 부족", "높은 변동성"],
            "immediate_actions": [
                {"action": "sell", "ticker": "005930", "quantity": 10, "reason": "비중 조절"}
            ],
            "risk_assessment": "시장 평균보다 다소 높은 리스크를 보이고 있습니다.",
            "long_term_strategy": "기술주 비중을 줄이고 배당주를 늘려 안정성을 확보하세요."
        }

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    holdings_str = "\n".join([f"- {h.ticker} ({h.name}): {h.quantity}주, 비중 {h.weight:.1f}%" for h in portfolio.holdings])
    
    prompt = f"""
    당신은 20년 경력의 전문 포트폴리오 매니저입니다.
    
    포트폴리오 정보:
    - 총 자산: {portfolio.total_value:,.0f}원
    - 종목 수: {len(portfolio.holdings)}개
    - 수익률: {portfolio.profit_rate:.2f}%
    
    보유 종목:
    {holdings_str}
    
    리스크 지표:
    - 리스크 점수: {risk_metrics['risk_score']}/10
    - 변동성: {risk_metrics['volatility']:.2f}%
    - 샤프 비율: {risk_metrics['sharpe_ratio']:.3f}
    
    섹터 분산:
    현재: {sector_analysis['current']}
    문제점: {sector_analysis['issues']}
    
    JSON 형식으로 분석 결과를 반환하세요.
    {{
      "summary": "종합 평가 (한글 3-4문장)",
      "strengths": ["강점1", "강점2", "강점3"],
      "weaknesses": ["약점1", "약점2", "약점3"],
      "immediate_actions": [
        {{"action": "sell", "ticker": "TICKER", "quantity": 10, "reason": "이유"}}
      ],
      "risk_assessment": "리스크 평가",
      "long_term_strategy": "장기 전략"
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "전문 포트폴리오 매니저"},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"OpenAI Error: {e}")
        return {"error": "AI Analysis Failed"}
