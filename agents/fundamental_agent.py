from .base_agent import BaseAgent
from typing import Dict, Any
import json

class FundamentalAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.system_prompt = """You are an expert fundamental analyst. Analyze the given stock based on:
        1. Financial ratios (P/E, P/B, ROE, etc.)
        2. Growth metrics (revenue growth, earnings growth)
        3. Financial health (debt levels, cash flow)
        4. Competitive position
        5. Management quality
        
        Return your analysis as a JSON object with the following structure:
        {
            "financial_health": float,  # Score from 0-1
            "growth_potential": float,  # Score from 0-1
            "competitive_position": float,  # Score from 0-1
            "management_quality": float,  # Score from 0-1
            "overall_score": float,  # Weighted average of above scores
            "key_strengths": List[str],
            "key_risks": List[str],
            "recommendation": "buy" | "hold" | "sell"
        }"""

    def analyze(self, ticker: str, context: Dict[str, Any]) -> Dict[str, Any]:
        user_prompt = f"""Analyze {ticker} based on fundamental factors.
        Consider the following context:
        - Risk tolerance: {context.get('risk_tolerance', 'moderate')}
        - Investment horizon: {context.get('investment_horizon', 'medium_term')}
        - Preferred sectors: {context.get('sectors', [])}
        """
        
        response = self.get_llm_response(self.system_prompt, user_prompt)
        return json.loads(response) 