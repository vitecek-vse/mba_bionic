from abc import ABC, abstractmethod
from typing import Dict, List, Any
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
import time
import random

class BaseAgent(ABC):
    def __init__(self):
        load_dotenv()
        self.client = AzureOpenAI(
            api_version="2024-12-01-preview",
            azure_endpoint="https://bionicadvisor.openai.azure.com/",
            api_key=os.getenv("AZURE_OPENAI_API_KEY")
        )
    
    @abstractmethod
    def analyze(self, ticker: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a given ticker and return investment insights
        Args:
            ticker: Stock ticker symbol
            context: Additional context including user preferences
        Returns:
            Dictionary containing analysis results
        """
        pass
    
    def get_llm_response(self, system_prompt: str, user_prompt: str) -> str:
        """
        Get response from Azure OpenAI with retry mechanism for rate limits
        """
        max_retries = 5
        base_delay = 2  # Base delay in seconds
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=4096,
                    temperature=0.7,
                    model="gpt-35-turbo",
                    response_format={ "type": "json_object" }  # Force JSON response
                )
                return response.choices[0].message.content
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"Rate limit hit. Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                else:
                    raise e 