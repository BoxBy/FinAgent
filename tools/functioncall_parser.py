import json
import logging
import re
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FunctionCallResult:
    function_name: str
    success: bool
    result: Any
    error_message: Optional[str] = None

class FunctionCallHandler:
    """Function call 처리를 담당,일반적인 LLM에서 사용가능"""
    def __init__(self, env_trading):
        """env_trading(EnvironmentTrading 인스턴스)로 초기화"""
        self.env_trading = env_trading
        # Function schema 정의 예시, 이렇게 하드 코딩하는 것은 좋지 않으나 일단 테스트 용이니까 파일 늘리지 않고 하드코딩함,description은 영어로 작성하면 한글보다 좋음
        # 제미니 경우는 FunctionDeclaration 로 펑션콜을 만들수 있음, 이러면 구글 sdk를 사용하기 때문에 구글에 종속됨
        self.function_schemas = [
            {
                "name": "get_stock_price",
                "description": "Get the current price of a specific stock",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock symbol (e.g., AAPL, GOOGL)"
                        }
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "buy_stock",
                "description": "Buy shares of a stock",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock symbol"
                        },
                        "quantity": {
                            "type": "integer",
                            "description": "Number of shares to buy"
                        }
                    },
                    "required": ["symbol", "quantity"]
                }
            },
            {
                "name": "sell_stock",
                "description": "Sell shares of a stock",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock symbol"
                        },
                        "quantity": {
                            "type": "integer",
                            "description": "Number of shares to sell"
                        }
                    },
                    "required": ["symbol", "quantity"]
                }
            },
            {
                "name": "get_portfolio",
                "description": "Get the current portfolio status",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
        self.function_mapping = {
            "get_stock_price": self._get_stock_price,
            "buy_stock": self._buy_stock,
            "sell_stock": self._sell_stock,
            "get_portfolio": self._get_portfolio
        }
    # 아래의 함수는 임의로 만든 것, 데이터셋 보고 다시 매칭 필요
    def _get_stock_price(self, symbol: str) -> Dict:
        
        price = self.env_trading.price
        return {
            "symbol": self.env_trading.symbol,
            "price": price,
            "currency": "USD",
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }

    def _buy_stock(self, symbol: str, quantity: int) -> Dict:
        try:
            price = self.env_trading.price
            # EnvironmentTrading 을 그대로 사용할려고 했음, EnvironmentTrading은 심볼을 사용하지 않음, 나중에 래퍼로 감싸야할수 있음
            # EnvironmentTrading의 고정된 self.symbol만 사용하고 있어서, 사용자가 다른 symbol을 요청해도 항상 같은 자산(AAPL)에 대해서만 거래가 이루어짐
            for _ in range(quantity):
                self.env_trading.buy(price, amount=1)
            return {
                "action": "buy",
                "symbol": self.env_trading.symbol,
                "quantity": quantity,
                "price": price,
                "status": "success",
                "cash": self.env_trading.cash,
                "position": self.env_trading.position,
                "value": self.env_trading.value
            }
        except Exception as e:
            return {
                "action": "buy",
                "symbol": self.env_trading.symbol,
                "quantity": quantity,
                "status": "error",
                "error": str(e)
            }

    def _sell_stock(self, symbol: str, quantity: int) -> Dict:
        try:
            price = self.env_trading.price
            for _ in range(quantity):
                self.env_trading.sell(price, amount=-1)
            return {
                "action": "sell",
                "symbol": self.env_trading.symbol,
                "quantity": quantity,
                "price": price,
                "status": "success",
                "cash": self.env_trading.cash,
                "position": self.env_trading.position,
                "value": self.env_trading.value
            }
        except Exception as e:
            return {
                "action": "sell",
                "symbol": self.env_trading.symbol,
                "quantity": quantity,
                "status": "error",
                "error": str(e)
            }

    def _get_portfolio(self) -> Dict:
        """포트폴리오 상태 조회 (EnvironmentTrading의 속성 사용)"""
        try:
            return {
                "cash": self.env_trading.cash,
                "position": self.env_trading.position,
                "value": self.env_trading.value,
                "symbol": self.env_trading.symbol,
                "status": "success"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def create_function_call_prompt(self, user_message: str, include_functions: bool = True) -> str:
        """
        Function call을 포함한 LLM용 프롬프트 생성
        
        Args:
            user_message: 사용자 메시지
            include_functions: 함수 정보 포함 여부
            
        Returns:
            str: LLM에 보낼 프롬프트
        """
        
        base_prompt = """You are a professional AI assistant specializing in stock trading.
You can perform the following tasks based on user requests:

1. Get current stock price
2. Buy stocks
3. Sell stocks
4. Check portfolio status

Please follow the exact format below when responding:

For general responses:
<response>
Write your general response here.
</response>

When you need to call a function:
<function_call>
{
    "name": "function_name",
    "parameters": {
        "param1": "value1",
        "param2": "value2"
    }
}
</function_call>"""

        if include_functions:
            functions_info = "\n\nAvailable functions:\n"
            for schema in self.function_schemas:
                functions_info += f"\n- {schema['name']}: {schema['description']}\n"
                if schema['parameters']['properties']:
                    functions_info += "  Parameters:\n"
                    for param_name, param_info in schema['parameters']['properties'].items():
                        required = " (required)" if param_name in schema['parameters'].get('required', []) else " (optional)"
                        functions_info += f"    - {param_name}: {param_info['description']}{required}\n"
            
            base_prompt += functions_info
        
        full_prompt = f"""{base_prompt}

User request: {user_message}

Please analyze the above request and either call an appropriate function or provide a general response."""

        return full_prompt
    
    def parse_llm_response(self, llm_response: str) -> Dict:
        """
        Parse function call from LLM response
        
        Args:
            llm_response: Response received from LLM
            
        Returns:
            Dict: Parsing result
        """
        try:
            # <function_call> 태그 찾기
            function_call_pattern = r'<function_call>\s*(.*?)\s*</function_call>'
            function_call_match = re.search(function_call_pattern, llm_response, re.DOTALL)
            
            if function_call_match:
                function_call_json = function_call_match.group(1).strip()
                try:
                    function_call_data = json.loads(function_call_json)
                    return {
                        "type": "function_call",
                        "function_call": function_call_data,
                        "raw_response": llm_response
                    }
                except json.JSONDecodeError as e:
                    logger.error(f"Function call JSON parsing error: {str(e)}")
                    return {
                        "type": "error",
                        "error": f"Function call JSON parsing failed: {str(e)}",
                        "raw_response": llm_response
                    }
            
            # <response> 태그 찾기
            response_pattern = r'<response>\s*(.*?)\s*</response>'
            response_match = re.search(response_pattern, llm_response, re.DOTALL)
            
            if response_match:
                response_text = response_match.group(1).strip()
                return {
                    "type": "text_response",
                    "content": response_text,
                    "raw_response": llm_response
                }
            
            # 태그가 없는 경우 전체 응답을 텍스트로 처리
            return {
                "type": "text_response",
                "content": llm_response.strip(),
                "raw_response": llm_response
            }
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            return {
                "type": "error",
                "error": f"Response parsing failed: {str(e)}",
                "raw_response": llm_response
            }
    
    def execute_function_call(self, function_call_data: Dict) -> FunctionCallResult:
        """
        Execute function call data
        
        Args:
            function_call_data: Parsed function call data
        
        Returns:
            FunctionCallResult: Execution result
        """
        try:
            function_name = function_call_data.get("name")
            parameters = function_call_data.get("parameters", {})
            
            logger.info(f"Function call execution: {function_name}, parameters: {parameters}")
            
            if function_name not in self.function_mapping:
                return FunctionCallResult(
                    function_name=function_name,
                    success=False,
                    result=None,
                    error_message=f"Unsupported function: {function_name}"
                )
            
            # 함수 실행
            function_to_call = self.function_mapping[function_name]
            result = function_to_call(**parameters)
            
            return FunctionCallResult(
                function_name=function_name,
                success=True,
                result=result
            )
        
        except Exception as e:
            logger.error(f"Error during function call execution: {str(e)}")
            return FunctionCallResult(
                function_name=function_call_data.get("name", "unknown"),
                success=False,
                result=None,
                error_message=str(e)
            )
    
    def process_user_request(self, user_message: str, llm_response: str) -> Dict:
        """
        Process complete user request (from prompt generation to function execution)
        
        Args:
            user_message: User message
            llm_response: LLM response
            
        Returns:
            Dict: Processing result
        """
        # 1. Parse LLM response
        parsed_response = self.parse_llm_response(llm_response)
        
        # 2. Execute if it's a function call
        if parsed_response["type"] == "function_call":
            function_result = self.execute_function_call(parsed_response["function_call"])
            
            return {
                "type": "function_executed",
                "user_message": user_message,
                "parsed_response": parsed_response,
                "function_result": function_result,
                "timestamp": datetime.now().isoformat()
            }
        
        # 3. For general text response
        elif parsed_response["type"] == "text_response":
            return {
                "type": "text_response", 
                "user_message": user_message,
                "content": parsed_response["content"],
                "timestamp": datetime.now().isoformat()
            }
        
        # 4. For error cases
        else:
            return {
                "type": "error",
                "user_message": user_message,
                "error": parsed_response.get("error", "Unknown error"),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_function_schemas(self) -> List[Dict]:
        """Return function schema list"""
        return self.function_schemas.copy()
    
    def reset_portfolio(self):
        """Reset portfolio (using EnvironmentTrading's reset method)"""
        self.env_trading.reset()
        logger.info("Portfolio has been reset.")

# Usage example and test function
def test_function_call_handler():
    """FunctionCallHandler test function"""
    print("=" * 60)
    print("📈 Function Call Handler Test")
    print("=" * 60)
    
    # Create EnvironmentTrading instance (example)
    class MockEnvironmentTrading:
        def __init__(self):
            self.cash = 100000.0
            self.position = 0
            self.value = 100000.0
            self.symbol = "AAPL"
            self.price = 175.43 # Initial price
            self.transactions = []

        def buy(self, price: float, amount: int):
            cost = price * amount
            if self.cash >= cost:
                self.cash -= cost
                self.position += amount
                self.value = self.cash + self.position * price
                self.transactions.append({
                    "type": "BUY",
                    "price": price,
                    "amount": amount,
                    "timestamp": datetime.now().isoformat()
                })
            else:
                raise ValueError("Insufficient balance.")

        def sell(self, price: float, amount: int):
            if self.position >= amount:
                self.position -= amount
                self.cash += price * amount
                self.value = self.cash + self.position * price
                if self.position == 0:
                    self.symbol = None # Remove symbol if no shares are held
                self.transactions.append({
                    "type": "SELL",
                    "price": price,
                    "amount": amount,
                    "timestamp": datetime.now().isoformat()
                })
            else:
                raise ValueError("Insufficient shares.")

        def get_status(self) -> Dict:
            return {
                "cash": self.cash,
                "position": self.position,
                "value": self.value,
                "symbol": self.symbol,
                "transaction_count": len(self.transactions)
            }

        def reset(self):
            self.cash = 100000.0
            self.position = 0
            self.value = 100000.0
            self.symbol = "AAPL"
            self.price = 175.43
            self.transactions = []

    env_trading = MockEnvironmentTrading()
    handler = FunctionCallHandler(env_trading)
    
    # 1. 프롬프트 생성 테스트
    print("\n1. Prompt Generation Test")
    user_message = "Please check the current price of AAPL"
    prompt = handler.create_function_call_prompt(user_message)
    print(f"Generated prompt (first 200 chars):\n{prompt[:200]}...")
    
    # 2. 모의 LLM 응답 파싱 테스트
    print("\n2. Function Call Parsing Test")
    mock_llm_response = '''<function_call>
{
    "name": "get_stock_price",
    "parameters": {
        "symbol": "AAPL"
    }
}
</function_call>'''
    
    parsed = handler.parse_llm_response(mock_llm_response)
    print(f"Parsing result: {parsed}")
    
    # 3. Function Call 실행 테스트
    print("\n3. Function Call Execution Test")
    if parsed["type"] == "function_call":
        result = handler.execute_function_call(parsed["function_call"])
        print(f"Execution result: {result.result}")
    
    # 4. 전체 프로세스 테스트
    print("\n4. Full Process Test")
    
    test_cases = [
        ("Please buy 10 shares of GOOGL", '''<function_call>
{
    "name": "buy_stock", 
    "parameters": {
        "symbol": "GOOGL",
        "quantity": 10
    }
}
</function_call>'''),
        
        ("Please check the portfolio status", '''<function_call>
{
    "name": "get_portfolio",
    "parameters": {}
}
</function_call>'''),
        
        ("Hello", '''<response>
Hello! How can I help you with stock trading?
</response>''')
    ]
    
    for user_msg, llm_resp in test_cases:
        print(f"\nUser: {user_msg}")
        result = handler.process_user_request(user_msg, llm_resp)
        print(f"Processing result: {result['type']}")
        if result['type'] == 'function_executed':
            print(f"Function execution result: {result['function_result'].result}")
        elif result['type'] == 'text_response':
            print(f"Text response: {result['content']}")

if __name__ == "__main__":
    test_function_call_handler()