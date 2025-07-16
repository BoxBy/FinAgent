import re
from typing import Any, Dict, List, Optional, Union, Tuple
import json

def analysis(
    latest_market_intelligence_summary_res: Dict[str, Any],
    type: str = "raw_data",
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """
    # Done:
    - `analysis()` 함수 구현: 시장 뉴스 입력을 받아 sentiment, momentum, impact_score, signal, reason 분석하는 prompt 설계
    - LLM 연동을 위한 `run_llm()` (더미 구현) 및 JSON 파싱용 `extract_json_from_text()` 추가
    - 위험 조건(sentiment ≤ -0.8 AND impact_score > 80) 시 emergency() 호출 트리거 구현
    - 기존 get_latest_market_intellgence(), emergency() 함수와 연동

    # ToDo & 고민해봐야 할 것 : 
    - 현재 run_llm()은 하드코딩된 더미 응답만 반환하므로 실제 LLM API 연동 필요
    - emergency() 기능 및 역할 정의와 구현 보완 필요
    - 트리거 점수 기준 다시 정할 필요 있을 듯 
    - finagent 분석 시작 시점과 흐름 제어 구조 고민 필요 (main.py 호출 방식 개선)
    """

    try:
        # 1. 시장 뉴스 가져옴
        market_text = get_latest_market_intellgence(latest_market_intelligence_summary_res, type=type)
        if not market_text:
            return {"error": "No market data found."}

        # 2. LLM모델에게 시장뉴스 넘겨줌
        semtiment_prompt = f"""
        You are a professional financial analyst tasked with analyzing news articles to assess their impact on the market. Based on the given news content, carefully evaluate and provide a JSON output with the following fields:

        {{
        "sentiment_score": float,    // Sentiment score ranging from -1 (very negative) to 1 (very positive)
        "market_momentum": string,   // One of: "bullish", "neutral", or "bearish"
        "impact_score": int,         // Integer from 0 to 100 indicating the potential impact on the market (0 = no impact, 100 = very high impact)
        "final_trading_signal": string, // One of: "BUY", "HOLD", or "SELL"
        "reason": string             // A brief explanation (2-3 sentences) supporting your assessments and final signal
        }}

        ---

        Guidelines to follow:

        1. Sentiment Score (-1 to 1):  
        Assign a numeric score representing the overall tone of the news.  
        -1 means extremely negative sentiment, 0 means neutral, and 1 means extremely positive sentiment.

        2. Market Momentum (bullish, neutral, bearish):  
        Determine the likely short-term market trend implied by the news.  
        "bullish" indicates upward momentum, "bearish" indicates downward momentum, and "neutral" means no clear directional movement.

        3. Impact Score (0 to 100):  
        Estimate how significantly this news could influence market behavior.  
        Consider the credibility of the source, the scale of the news (e.g., company-specific vs. economy-wide), and timing relevance.

        4. Final Trading Signal (BUY, HOLD, SELL):  
        Based on the combined assessment of sentiment, momentum, and impact, recommend a trading action.  
        "BUY" suggests positive outlook, "SELL" suggests caution or expected decline, "HOLD" means no immediate action.

        5. Reason:  
        Provide a concise summary explaining the rationale behind the sentiment score, momentum, impact score, and trading signal.

        ---

        News Content:  
        {market_text}

        Please respond ONLY with the JSON object in the exact format above.

        """

        llm_result = run_llm(semtiment_prompt, model)
        if llm_result is None:
            return {"error": "No LLM."}

        # 3. 결과 파싱
        sentiment, momentum, impact_score,signal, reason = extract_json_from_text(llm_result)

        result = {
            "sentiment": sentiment,
            "momentum": momentum,
            "impact_score": impact_score,
            "signal": signal,
            "reason": reason
        }

        print(f"[Sentiment Analysis LLM Result] {result}")
        
        # 4. 위험 상황 시 emergency 호출 (emergece 함수역할 명확하지않아, 우선 trigger역할로 임의 설정함) 

        if sentiment <= -0.8 and impact_score > 80:
            emergency()
            print("="*50)
            print("⚠️ Emergency Trigger Activated! → ⛔ Finagent 실행")
            print(f"Signal: {signal}, Reason: {reason}")
            print("="*50)

        return result

    except Exception as e:
        return {"error": str(e)}


def get_latest_market_intellgence(latest_market_intelligence_summary_res, type="raw_data") -> Union[List, str]:
# 뉴스 가져오는 클래스 : FinAgent/finagent/prompt/trading/latest_market_intelligence_summary.py
    # prompt 폴더에 있는거로 보아 내부에서 prompt화를 하나봅니다
    # FinAgent/finagent/prompt/custom.py에 있는 Prompt를 상속받아 다시 작성해도 됨
    """
    최신 시장 정보와 뉴스를 가져와서 반환하는 함수
    
    Returns:
        Union[List, str]: 뉴스 리스트 또는 요약된 문자열
    """
    try:
        # LatestMarketIntelligenceSummary 클래스 인스턴스 생성
        # market_intelligence = LatestMarketIntelligenceSummary()
        
        # 최신 시장 정보 가져오기
        # get_response_dict 메서드를 사용하여 결과 얻기
        # response = market_intelligence.get_response_dict()
        """
        res = {
            "params": task_params,
            "message": message,
            "html": html,
            "res_html": res_html,
            "response_dict": response_dict,
        }
        response_dict = [
            "query", # 분석을 위한 질문, 요청
            "summary" # 분석내용
        ]
        """
        if type == "raw_data":
            # type1. 뉴스 정보를 가져오는 경우 (price, news --> pram)
                # latest_market_intelligence_summary.convert_to_params은 price와 news를 시장 state 정보를 가진 text로 변환해 저장함
            latest_market_intelligence_text = latest_market_intelligence_summary_res["params"]["latest_market_intelligence"]
            return latest_market_intelligence_text
        elif type == "market_intelligence_summary":
            # type2.  market_intelligence_summary를 가져오는 경우
            latest_market_intelligence_response_dict = latest_market_intelligence_summary_res["response_dict"]

            # 응답이 딕셔너리 형태라면 필요한 데이터 추출
            if isinstance(latest_market_intelligence_response_dict, dict):
                if 'summary' in latest_market_intelligence_response_dict:
                    return latest_market_intelligence_response_dict['summary']
                elif 'query' in latest_market_intelligence_response_dict:
                    return latest_market_intelligence_response_dict['query']
                else:
                    # 전체 응답을 문자열로 반환
                    return str(latest_market_intelligence_response_dict)
            
            # 문자열이나 리스트 형태라면 그대로 반환
            return latest_market_intelligence_response_dict
    
        else:
            raise ValueError("Invalid type specified. Use 'raw_data' or 'market_intelligence_summary'.")
                
    except Exception as e:
        print(f"뉴스 가져오기 실패: {e}")
        return f"Error: {str(e)}"

    # pass

def emergency():
    pass
    # function call용 함수
    # main.py - L384에서 decision합니다 참고하세요

def run_llm(prompt: str, model: Optional[str] = None) -> str:
    
    # llm 어떤거쓸지 구현 등 설정 필요함

    return """
    {
        "sentiment": -0.9,
        "momentum": "bearish",
        "impact_score": 85,
        "signal": "SELL",
        "reason": "Company earnings missed expectations and interest rate concerns increase risk."
    }
    """

def extract_json_from_text(text: str) -> Tuple[float, str, int, str, str]:
    """
    Extract JSON fields from LLM response text.
    Returns: sentiment (float), momentum (str), impact_score (int), signal (str), reason (str)
    """

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # 2. 정규식으로 {...} 부분만 추출
        match = re.search(r"\{.*\}", text, flags=re.S)
        if match:
            snippet = match.group(0)
            try:
                data = json.loads(snippet)
            except json.JSONDecodeError:
                data = {}
        else:
            data = {}

    sentiment = float(data.get("sentiment", 0.0))
    momentum = str(data.get("momentum", "neutral"))
    impact_score = int(data.get("impact_score", 0))
    signal = str(data.get("signal", "HOLD"))
    reason = str(data.get("reason", "No reason provided."))

    return sentiment, momentum, impact_score, signal, reason

# 테스트
if __name__ == "__main__":
    latest_market_intelligence_summary_res = {
        "params": {
            "latest_market_intelligence": "Tech stocks fell sharply after disappointing earnings reports and inflation concerns."
        }
    }

    result = analysis(latest_market_intelligence_summary_res, type="raw_data", model="gpt-4")
    print(result)
