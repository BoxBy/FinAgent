from typing import Union, List, Dict, Any, Tuple
from finagent.prompt import custom
import logging
import json   
import re
# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalysisPrompt(custom.Prompt):
    "Sentiment Analysis를 위한 커스텀 프롬프트 클래스"
    def __init__(self, model="gpt-4preview"):
        super().__init__(model=model)
    
    def create_sentiment_analysis_prompt(self, market_intelligence: str) -> str:
        #   분석을 위한 프롬프트 생성 
        trigger_prompt = f"""
        You are an event-driven financial analyst. Your TOP priority is to decide whether the provided news should be treated as a **market-triggering emergence event** (binary: 1 or 0). After making that judgment, provide supporting market analytics.

        Return ONLY a valid JSON object with the exact fields shown below (no extra text).

        {{
        "emergence": int,                // 1 if this news is NEW, MATERIAL, and likely to TRIGGER short-term market repricing; else 0
        "sentiment_score": float,        // -1 to 1
        "market_momentum": string,       // "bullish", "neutral", or "bearish"
        "impact_score": int,             // 0-100 potential market impact
        "final_trading_signal": string,  // "BUY", "HOLD", or "SELL"
        "reason": string                 // 2-3 sentences: why emergence? how sentiment & impact led to signal
        }}

        ----------------
        How to judge **emergence** (trigger focus):

        Set emergence = 1 ONLY if MOST of the following apply:
        - **Materiality**: News could meaningfully affect valuation, liquidity, regulation, or operations.
        - **Immediacy**: Near-term catalyst (effective now or within a short, market-relevant window).
        - **Surprise vs Expectation**: Not widely expected, not just a routine or incremental update.
        - **Actionability**: Traders would care NOW (earnings shock, guidance cut/raise, M&A announcement, regulatory approval/ban, fraud exposure, major macro policy shift).

        Set emergence = 0 if:
        - Already known, previously announced, or widely expected.
        - Incremental commentary, opinion, or long-running story without new actionable development.
        - Data lacks timing clarity or market linkage.

        ----------------
        Other fields (fill even if emergence=0):

        1. Sentiment Score (-1..1): Tone of the development for the affected asset(s) or market.
        2. Market Momentum: Short-term directional implication (bullish / neutral / bearish).
        3. Impact Score (0..100): Potential magnitude of market influence (scope, credibility, timing).
        4. Final Trading Signal: BUY / HOLD / SELL, integrating all above. Emergence=1 with high impact may tilt toward more decisive action.
        5. Reason: Brief explanation tying together emergence judgment, sentiment, impact, and resulting signal.

        ----------------
        News Content:
        {market_intelligence}

        Respond ONLY with JSON.
        """
        return trigger_prompt
    
    def analyze_sentiment(self, market_intelligence: str, provider) -> Dict[str, Any]:
        # 감정 분석 실행     
        prompt = self.create_sentiment_analysis_prompt(market_intelligence)
        response = self.get_response_dict(messages=prompt, provider=provider) # LLM 실행한다고 가정
        emergence, sentiment, momentum, impact_score, signal, reason = extract_json_from_text(response)
        result = {
            "emergence": emergence,
            "sentiment": sentiment,
            "momentum": momentum,
            "impact_score": impact_score,
            "signal": signal,
            "reason": reason
        }

        logger.info(f"Sentiment Analysis Result: {result}")

        return result


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
    emergence= int(data.get("emergence", 0))
    sentiment = float(data.get("sentiment", 0.0))
    momentum = str(data.get("momentum", "neutral"))
    impact_score = int(data.get("impact_score", 0))
    signal = str(data.get("signal", "HOLD"))
    reason = str(data.get("reason", "No reason provided."))

    return emergence, sentiment, momentum, impact_score, signal, reason

def get_latest_market_intelligence(latest_market_intelligence_summary_res, type="raw_data") -> Union[List, str]:
    '''최신 시장 정보와 뉴스를 가져와서 반환하는 함수
    
    Args:
        latest_market_intelligence_summary_res: Latest market intelligence 결과
        type: 데이터 타입 ("raw_data" 또는 "market_intelligence_summary")
    
    Returns:
        Union[List, str]: 뉴스 리스트 또는 요약된 문자열   '''
    try:
        if type == "raw_data":
            # type1. 뉴스 정보를 가져오는 경우 (price, news --> param)
            latest_market_intelligence_text = latest_market_intelligence_summary_res["params"]["latest_market_intelligence"]
            return latest_market_intelligence_text
            
        elif type == "market_intelligence_summary":
            # type2. market_intelligence_summary를 가져오는 경우
            latest_market_intelligence_response_dict = latest_market_intelligence_summary_res["response_dict"]

            # 응답이 딕셔너리 형태라면 필요한 데이터 추출
            if isinstance(latest_market_intelligence_response_dict, dict):
                if 'summary in latest_market_intelligence_response_dict':
                    return latest_market_intelligence_response_dict['summary']              
                elif "query" in latest_market_intelligence_response_dict:
                    return latest_market_intelligence_response_dict['query']              
                else:
                    # 전체 응답을 문자열로 반환
                    return str(latest_market_intelligence_response_dict)
            
            # 문자열이나 리스트 형태라면 그대로 반환
            return latest_market_intelligence_response_dict
    
        else:
            raise ValueError("Invalid type specified. Use 'raw_data' or 'market_intelligence_summary'.")
                
    except Exception as e:
        logger.error(f"Failed to get market intelligence: {e}")
        return f"Error: {str(e)}"

def emergency():
    """Emergency function for function call integration"""
    return {
        "type": "emergency",
        "message": "Emergency function called",
        "status": "success"
    }

# Function Call Handler와 통합을 위한 함수들
def get_sentiment_analysis_functions() -> List[Dict]:
    """function Call Handler용 감정 분석 함수 스키마 반환"""
    # return [
    #     {
    #     "name":"analyze_market_sentiment",
    #     "description": "Analyze market sentiment based on latest market intelligence",
    #     "parameters" : {
    #         "type" : "object",
    #         "properties" : {
    #             "expr" : {
    #                 "type" : "string",
    #                 "decsription" : "Data type for analysis",
    #                 "enum" : ["raw_data", "market_intelligence_summary"],
    #             },
    #         },
    #         "required" : ["type"],
    #     }
    # },
    #     {
    #         "name" : "emergency_action",
    #         "description" : "Execute emergency action",
    #         "parameters" : {
    #             "type" : "object",
    #             "properties" : {
    #                 "expr" : {
    #                     "type" : "bool", # bool? boolean?
    #                 }
    #             }
    #         }
    #     }
    # ]


# def execute_sentiment_function(function_name: str, parameters: Dict, market_intelligence_data: Dict) -> Dict[str, Any]:
#     """Function Call Handler에서 호출할 감정 분석 함수 실행"""   
#     try:
#         if function_name == "analyze_market_sentiment":
#             data_type = parameters.get("type", "raw_data")
#             return analysis(market_intelligence_data, data_type)
            
#         elif function_name == "emergency_action":
#             return emergency()
            
#         else:
#             return{
#                 "error" : f"Unknown function: {function_name}",
#                 "status" : "error"
#             }
            
#     except Exception as e:
#         logger.error(f"Function execution error: {str(e)}")
#         return {
#             "error" : str(e),
#             "status": "error" 
#         }
        
def analysis(latest_market_intelligence_summary_res, provider, type="raw_data") -> Tuple: # (boolean, Dict)
    """Sentiment Analysis 메인 함수
    
    Args:
        latest_market_intelligence_summary_res: Latest market intelligence 결과
        type: 데이터 타입 ("raw_data" 또는 "market_intelligence_summary")
    
    Returns:
        boolean = 실행여부
        Dict = decision.run()의 args들, boolean=False라면 None # 혹은 decision.run()의 인자를 전부 받아서 여기서 실행해도 됨
    """
    # Get latest market intelligence
    latest_market_intelligence = get_latest_market_intelligence(latest_market_intelligence_summary_res, type)
    print(f"Market Intelligence: {latest_market_intelligence}")
    
    # Create sentiment analysis prompt and analyze
    sentiment_analyzer = SentimentAnalysisPrompt()
    sentiment_result = sentiment_analyzer.analyze_sentiment(latest_market_intelligence, provider)
    sentiment_analysis_info =  {
        type: "sentiment_analysis",
        "market_intelligence": latest_market_intelligence,
        "sentiment_result": sentiment_result,
        "status":"success",
    }

    return sentiment_analysis_info, sentiment_result.get("emergence", 0) == 1  # emergence가 1이면 True, 아니면 False
