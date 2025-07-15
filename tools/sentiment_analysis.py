from typing import Union, List
from finagent.prompt import custom

def analysis(latest_market_intelligence, ): # 받아야 하는 인자가 있다면 추가하세요
    '''
    알고있어야 하는것들
    이 agent는 real-time이 아닌것으로 보입니다(딥하게 안봐서 틀릴수도 있음)
    tools/main.py - run_step(L228)을 무한루프하는 형식
    latest market intelligence는 이미 함수가 있습니다
    
    심지어 Agent는 Class도 아닙니다
    '''
    
    
    
    
    # Prompt는 custom.Prompt를 상속받아 작성하면 됨
    # model 호출은 FinAgent/finagent/prompt/custom.py - get_response_dict(L105)에 있습니다
    
def get_latest_market_intellgence() -> Union[List, str]:
# 뉴스 가져오는 클래스 : FinAgent/finagent/prompt/trading/latest_market_intelligence_summary.py
    # prompt 폴더에 있는거로 보아 내부에서 prompt화를 하나봅니다
    # FinAgent/finagent/prompt/custom.py에 있는 Prompt를 상속받아 다시 작성해도 됨
    pass

def emergency():
    pass
    # function call용 함수
    # main.py - L384에서 decision합니다 참고하세요