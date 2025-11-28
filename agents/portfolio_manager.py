from .base_agent import BaseAgent
from typing import Dict, Any, List
import json

class PortfolioManager(BaseAgent):
    def __init__(self):
        super().__init__()
        self.system_prompt = """You are an expert portfolio manager. Based on the analyses provided and user preferences,
        create an optimal portfolio allocation. You MUST return a valid JSON object, nothing else.
        
        Prioritize including a diverse set of tickers, aiming for a portfolio of up to 30 stocks if sufficient analyses are provided. Ensure the weights assigned to each stock are varied based on your analysis, rather than being uniform.

        Example of the required JSON structure:
        {
            "portfolio": [
                {
                    "ticker": "AAPL",
                    "weight": 0.25,
                    "rationale": "Strong financial health and growth"
                }
            ],
            "expected_return": 0.12,
            "risk_score": 0.6,
            "diversification_score": 0.8,
            "sector_allocation": {
                "technology": 0.75,
                "healthcare": 0.25
            },
            "key_risks": [
                "Supply chain disruptions",
                "Regulatory risks"
            ]
        }

        Important: Return ONLY the JSON object, no additional text or formatting."""

    def analyze(self, tickers: List[str], analyses: Dict[str, Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        user_prompt = f"""Create a portfolio allocation based on the following:
        
        User Preferences:
        - Risk tolerance: {context.get('risk_tolerance', 'moderate')}
        - Investment horizon: {context.get('investment_horizon', 'medium_term')}
        - Preferred sectors: {context.get('sectors', [])}
        
        Stock Analyses:
        {json.dumps(analyses, indent=2)}

        Please create a diversified portfolio from the provided stocks. Aim to include between 20 and 30 stocks from the analyzed list, distributing the weights optimally. Ensure weights are not identical.

        Remember: Return ONLY a valid JSON object matching the example structure above."""
        
        response = self.get_llm_response(self.system_prompt, user_prompt)
        print("\n[DEBUG] Raw LLM response for portfolio manager:\n", response)
        try:
            print(response)
            return json.loads(response)
        except json.JSONDecodeError as e:
            print("\n[ERROR] Failed to parse LLM response as JSON:")
            print(response)
            raise e 