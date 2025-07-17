from typing import Union, List, Dict, Any
from finagent.prompt import custom
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalysisPrompt(custom.Prompt):
    """Sentiment Analysis를 위한 커스텀 프롬프트 클래스
    def __init__(self, model="gpt-4preview"):
        super().__init__(model=model)
    
    def create_sentiment_analysis_prompt(self, market_intelligence: str) -> str:
      분석을 위한 프롬프트 생성        prompt = f"""You are a financial sentiment analysis expert. 
Analyze the following market intelligence and provide sentiment analysis:

Market Intelligence:
{market_intelligence}

Please provide sentiment analysis in the following format:

<sentiment_analysis>
{{
    overall_sentiment": positive/negative/neutral,confidence_score": 0.85,
   key_factors":        factor1,
        factor2,
       factor3],
    risk_level": "low/medium/high",
   recommendation":buy/hold/sell",
   summary":Brief summary of sentiment analysis"
}}
</sentiment_analysis>     return prompt
    
    def analyze_sentiment(self, market_intelligence: str) -> Dict[str, Any]:
     정 분석 실행     prompt = self.create_sentiment_analysis_prompt(market_intelligence)
        response = self.get_response_dict(prompt)
        
        # 응답 파싱
        try:
            import re
            import json
            
            # <sentiment_analysis> 태그에서 JSON 추출
            pattern = r'<sentiment_analysis>\s*(.*?)\s*</sentiment_analysis>'
            match = re.search(pattern, response, re.DOTALL)
            
            if match:
                sentiment_data = json.loads(match.group(1).strip())
                return sentiment_data
            else:
                # 태그가 없는 경우 전체 응답을 파싱 시도
                return {"raw_response": response, "error": "No sentiment analysis tags found"}
                
        except Exception as e:
            logger.error(f"Sentiment analysis parsing error: {str(e)}")
            return {error: fParsing failed: {str(e)}", "response": response}

def analysis(latest_market_intelligence_summary_res, type="raw_data") -> Dict[str, Any]:
    """Sentiment Analysis 메인 함수
    
    Args:
        latest_market_intelligence_summary_res: Latest market intelligence 결과
        type: 데이터 타입 ("raw_data" 또는 "market_intelligence_summary")
    
    Returns:
        Dict[str, Any]: 감정 분석 결과    try:
        # Get latest market intelligence
        latest_market_intelligence = get_latest_market_intellgence(latest_market_intelligence_summary_res, type)
        print(f"Market Intelligence: {latest_market_intelligence}")
        
        # Create sentiment analysis prompt and analyze
        sentiment_analyzer = SentimentAnalysisPrompt()
        sentiment_result = sentiment_analyzer.analyze_sentiment(latest_market_intelligence)
        
        return {
            type": "sentiment_analysis",
     market_intelligence": latest_market_intelligence,
           sentiment_result": sentiment_result,
            status":success"
        }
        
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {str(e)}")
        return {
            type": "sentiment_analysis",
           errortr(e),
            status: error"
        }

def get_latest_market_intellgence(latest_market_intelligence_summary_res, type="raw_data") -> Union[List, str]:
    최신 시장 정보와 뉴스를 가져와서 반환하는 함수
    
    Args:
        latest_market_intelligence_summary_res: Latest market intelligence 결과
        type: 데이터 타입 ("raw_data" 또는 "market_intelligence_summary")
    
    Returns:
        Union[List, str]: 뉴스 리스트 또는 요약된 문자열   try:
        if type == "raw_data":
            # type1. 뉴스 정보를 가져오는 경우 (price, news --> param)
            latest_market_intelligence_text = latest_market_intelligence_summary_res["params"][latest_market_intelligence"]
            return latest_market_intelligence_text
            
        elif type == "market_intelligence_summary":
            # type2. market_intelligence_summary를 가져오는 경우
            latest_market_intelligence_response_dict = latest_market_intelligence_summary_res[response_dict"]

            # 응답이 딕셔너리 형태라면 필요한 데이터 추출
            if isinstance(latest_market_intelligence_response_dict, dict):
                if 'summary in latest_market_intelligence_response_dict:
                    return latest_market_intelligence_response_dict['summary]              elifquery in latest_market_intelligence_response_dict:
                    return latest_market_intelligence_response_dict['query]              else:
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
    return[object Object]
        type": "emergency",
  message": "Emergency function called,
        status": success
    }

# Function Call Handler와 통합을 위한 함수들
def get_sentiment_analysis_functions() -> List[Dict]:
  ction Call Handler용 감정 분석 함수 스키마 반환"""
    return [
     [object Object]
            name:analyze_market_sentiment",
          description: e market sentiment based on latest market intelligence",
          parameters[object Object]
                type,
              properties           type                   type                 description": "Data type for analysis",
                        enum": ["raw_data", "market_intelligence_summary"]
                    }
                },
                required": ["type"]
            }
        },
     [object Object]
            nameemergency_action",
          description": Execute emergency action",
          parameters[object Object]
                type,
               properties":[object Object]         }
        }
    ]

def execute_sentiment_function(function_name: str, parameters: Dict, market_intelligence_data: Dict) -> Dict[str, Any]:
  ction Call Handler에서 호출할 감정 분석 함수 실행""   try:
        if function_name ==analyze_market_sentiment":
            data_type = parameters.get("type", "raw_data")
            return analysis(market_intelligence_data, data_type)
            
        elif function_name ==emergency_action":
            return emergency()
            
        else:
            return[object Object]
                errorfUnknown function: {function_name},
                statuserror"
            }
            
    except Exception as e:
        logger.error(f"Function execution error: {str(e)}")
        return {
           errortr(e),
            status:error 