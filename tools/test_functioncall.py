#!/usr/bin/env python3
"""
Function Call Handler Test Script

Usage:
python tools/test_functioncall.py
"""

import sys
import os
from pathlib import Path

# Add project root path to Python path
ROOT = str(Path(__file__).resolve().parents[1])
sys.path.append(ROOT)

from tools.functioncall_parser import FunctionCallHandler, test_function_call_handler
from finagent.environment.trading import EnvironmentTrading

# Test dummy dataset/parameters need to be set (modify according to actual environment)
class DummyDataset:
    def __init__(self):
        import pandas as pd
        now = pd.Timestamp('2024-01-01')
        self.prices = {"AAPL": pd.DataFrame({"timestamp": [now], "open": [100], "high": [110], "low": [90], "close": [105], "adj_close": [105]})}
        self.news = {"AAPL": pd.DataFrame({"timestamp": [now], "id": [1], "title": ["Test News"], "text": ["Test content"]})}
        self.guidances = None
        self.sentiments = None
        self.economics = None

def get_env_trading():
    # Adjust parameters according to actual environment
    dataset = DummyDataset()
    env = EnvironmentTrading(
        mode="test",
        dataset=dataset,
        selected_asset="AAPL",
        asset_type="company",
        start_date="2024-01-01",
        end_date="2024-01-01",
        look_back_days=1,
        look_forward_days=1,
        initial_amount=100000,
        transaction_cost_pct=0.001,
        discount=1.0
    )
    return env

def interactive_test():
    """Interactive test function"""
    print("=" * 60)
    print("📈 Stock Agent Function Call Handler Test (EnvironmentTrading based)")
    print("=" * 60)
    env = get_env_trading()
    handler = FunctionCallHandler(env)
    
    try:
        # Handler initialization
        print("✅ FunctionCallHandler initialization completed")
        
        while True:
            print("\n" + "-" * 40)
            print("Test Menu:")
            print("1. Prompt Generation Test")
            print("2. LLM Response Parsing Test")
            print("3. Function Call Execution Test")
            print("4. Full Process Test")
            print("5. Portfolio Status Check")
            print("6. Auto Test Execution")
            print("7. Portfolio Reset")
            print("0. Exit")
            
            choice = input("\nSelect (0-7): ").strip()
            
            if choice == "0":
                print("Exiting test.")
                break
            
            elif choice == "1":
                user_message = input("Enter user message: ").strip()
                prompt = handler.create_function_call_prompt(user_message)
                print(f"\n📝 Generated prompt:")
                print("-" * 40)
                print(prompt)
                print("-" * 40)
            
            elif choice == "2":
                llm_response = input("Enter LLM response: ").strip()
                if not llm_response:
                    # Use example response
                    llm_response = '''<function_call>
{
    "name": "get_stock_price",
    "parameters": {
        "symbol": "AAPL"
    }
}
</function_call>'''
                    print("Using example response.")
                
                parsed = handler.parse_llm_response(llm_response)
                print(f"🔍 Parsing result: {parsed}")
            
            elif choice == "3":
                print("Enter Function Call data (JSON format):")
                print("Example: {\"name\": \"get_stock_price\", \"parameters\": {\"symbol\": \"AAPL\"}}")
                
                try:
                    function_data_str = input("Function Call data: ").strip()
                    if not function_data_str:
                        function_data = {
                            "name": "get_stock_price", 
                            "parameters": {"symbol": "AAPL"}
                        }
                        print("Using example data.")
                    else:
                        import json
                        function_data = json.loads(function_data_str)
                    
                    result = handler.execute_function_call(function_data)
                    print(f"⚡ Execution result:")
                    print(f"  Success: {result.success}")
                    print(f"  Result: {result.result}")
                    if result.error_message:
                        print(f"  Error: {result.error_message}")
                
                except Exception as e:
                    print(f"❌ Input processing error: {str(e)}")
            
            elif choice == "4":
                user_message = input("User message: ").strip()
                llm_response = input("LLM response: ").strip()
                
                if not user_message or not llm_response:
                    user_message = "Please buy 5 shares of MSFT"
                    llm_response = '''<function_call>
{
    "name": "buy_stock",
    "parameters": {
        "symbol": "MSFT",
        "quantity": 5
    }
}
</function_call>'''
                    print("Using example data.")
                
                result = handler.process_user_request(user_message, llm_response)
                print(f"🔄 Full processing result:")
                print(f"  Type: {result['type']}")
                if result['type'] == 'function_executed':
                    func_result = result['function_result']
                    print(f"  Function: {func_result.function_name}")
                    print(f"  Success: {func_result.success}")
                    print(f"  Result: {func_result.result}")
                elif result['type'] == 'text_response':
                    print(f"  Response: {result['content']}")
                elif result['type'] == 'error':
                    print(f"  Error: {result['error']}")
            
            elif choice == "5":
                result = handler.execute_function_call({
                    "name": "get_portfolio",
                    "parameters": {}
                })
                
                if result.success:
                    portfolio = result.result
                    print(f"📈 Portfolio status:")
                    print(f"  Cash: ${portfolio.get('cash', 0):,.2f}")
                    print(f"  Holdings:")
                    
                    for symbol, info in portfolio.get('holdings', {}).items():
                        print(f"    {symbol}: {info['quantity']} shares @ ${info['current_price']:.2f} = ${info['total_value']:,.2f}")
                    
                    print(f"  Total portfolio value: ${portfolio.get('total_portfolio_value', 0):,.2f}")
                    print(f"  Transaction count: {portfolio.get('transaction_count', 0)}")
                else:
                    print(f"❌ Portfolio query failed: {result.error_message}")
            
            elif choice == "6":
                print("🧪 Running auto test...")
                test_function_call_handler()
            
            elif choice == "7":
                handler.reset_portfolio()
                print("🔄 Portfolio has been reset.")
            
            else:
                print("❌ Please select a valid number.")
    
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")

def demo_scenarios():
    """Demo scenario execution"""
    print("\n" + "=" * 60)
    print("🚀 Stock Trading Agent Demo Scenarios")
    print("=" * 60)
    env = get_env_trading()
    handler = FunctionCallHandler(env)
    
    try:
        scenarios = [
            {
                "user_message": "Please check the current price of AAPL",
                "llm_response": '''<function_call>
{
    "name": "get_stock_price",
    "parameters": {
        "symbol": "AAPL"
    }
}
</function_call>'''
            },
            {
                "user_message": "Please buy 10 shares of GOOGL",
                "llm_response": '''<function_call>
{
    "name": "buy_stock",
    "parameters": {
        "symbol": "GOOGL",
        "quantity": 10
    }
}
</function_call>'''
            },
            {
                "user_message": "Please check the portfolio status",
                "llm_response": '''<function_call>
{
    "name": "get_portfolio",
    "parameters": {}
}
</function_call>'''
            },
            {
                "user_message": "Please sell 3 shares of GOOGL",
                "llm_response": '''<function_call>
{
    "name": "sell_stock",
    "parameters": {
        "symbol": "GOOGL",
        "quantity": 3
    }
}
</function_call>'''
            },
            {
                "user_message": "Hello! Please tell me about stock investment",
                "llm_response": '''<response>
Hello! Stock investment is a method of investing by purchasing shares of companies to earn profits along with the growth of those companies. 
Risk management and diversification are important, and it's good to approach it from a long-term perspective.
</response>'''
            }
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n📝 Scenario {i}: {scenario['user_message']}")
            print(f"LLM response: {scenario['llm_response'][:50]}...")
            
            result = handler.process_user_request(scenario['user_message'], scenario['llm_response'])
            
            if result['type'] == 'function_executed':
                func_result = result['function_result']
                if func_result.success:
                    print(f"✅ Function execution successful: {func_result.function_name}")
                    print(f"   Result: {func_result.result}")
                else:
                    print(f"❌ Function execution failed: {func_result.error_message}")
            elif result['type'] == 'text_response':
                print(f"💬 Text response: {result['content'][:100]}...")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"❌ Error during demo execution: {str(e)}")

def prompt_generation_demo():
    """Prompt generation demo"""
    print("\n" + "=" * 60)
    print("📝 Prompt Generation Demo")
    print("=" * 60)
    env = get_env_trading()
    handler = FunctionCallHandler(env)
    
    test_messages = [
        "Please check the current price of AAPL",
        "I want to buy 20 shares of Tesla",
        "I'm curious about my portfolio status",
        "Please give me advice on stock investment"
    ]
    
    for message in test_messages:
        print(f"\nUser message: {message}")
        prompt = handler.create_function_call_prompt(message)
        print(f"Generated prompt:\n{prompt}")
        print("-" * 40)

def test_function_call_handler_auto():
    env = get_env_trading()
    handler = FunctionCallHandler(env)
    test_function_call_handler()

if __name__ == "__main__":
    print("Starting Function Call Handler test...")
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "demo":
            demo_scenarios()
        elif sys.argv[1] == "prompt":
            prompt_generation_demo()
        elif sys.argv[1] == "auto":
            test_function_call_handler_auto()
        else:
            print("Usage: python test_functioncall.py [demo|prompt|auto]")
    else:
        interactive_test() 