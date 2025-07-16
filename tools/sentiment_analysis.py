from typing import Union, List
from finagent.prompt import custom

def analysis(latest_market_intelligence_summary_res, type="raw_data"): # 받아야 하는 인자가 있다면 추가하세요
    '''
    알고있어야 하는것들
    이 agent는 real-time이 아닌것으로 보입니다(딥하게 안봐서 틀릴수도 있음)
    tools/main.py - run_step(L228)을 무한루프하는 형식
    latest market intelligence는 이미 함수가 있습니다
    
    심지어 Agent는 Class도 아닙니다
    '''

    # get latest market intelligence
    latest_market_intelligence = get_latest_market_intellgence(latest_market_intelligence_summary_res, type)
    print(latest_market_intelligence)
    
    # Prompt는 custom.Prompt를 상속받아 작성하면 됨
    # model 호출은 FinAgent/finagent/prompt/custom.py - get_response_dict(L105)에 있습니다
    
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