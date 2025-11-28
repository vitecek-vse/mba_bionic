import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import json
from agents.fundamental_agent import FundamentalAgent
from agents.portfolio_manager import PortfolioManager

def get_investment_profile(client):
    """Get investment profile using Azure OpenAI"""
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": """You are a financial advisor assistant. Create an investment profile based on the following preferences:
                - Risk tolerance: moderate
                - Investment horizon: medium_term
                - Preferred sectors: technology, healthcare
                
                Return the profile as a JSON object with these exact fields:
                {
                    "risk_tolerance": "moderate",
                    "investment_horizon": "medium_term",
                    "sectors": ["technology", "healthcare"]
                }"""
            },
            {
                "role": "user",
                "content": "Create an investment profile."
            }
        ],
        max_tokens=4096,
        temperature=0.7,
        model="gpt-35-turbo"
    )
    
    return response.choices[0].message.content

def analyze_stocks(tickers: list, context: dict) -> dict:
    """Analyze stocks using the fundamental agent"""
    fundamental_agent = FundamentalAgent()
    analyses = {}
    
    for ticker in tickers:
        print(f"\n📊 Analyzing {ticker}...")
        analysis = fundamental_agent.analyze(ticker, context)
        analyses[ticker] = analysis
        print(f"Analysis complete for {ticker}")
    
    return analyses

def generate_portfolio(tickers: list, analyses: dict, context: dict) -> dict:
    """Generate portfolio using the portfolio manager"""
    portfolio_manager = PortfolioManager()
    print("\n🎯 Generating portfolio allocation...")
    portfolio = portfolio_manager.analyze(tickers, analyses, context)
    return portfolio

def main():
    # Load environment variables
    load_dotenv()
    
    # Azure OpenAI Configuration
    endpoint = "https://bionicadvisor.openai.azure.com/"
    deployment = "gpt-35-turbo"
    api_version = "2024-12-01-preview"
    
    print("🤖 Initializing Bionic Advisor...")
    
    try:
        # Initialize Azure OpenAI client
        client = AzureOpenAI(
            api_version=api_version,
            azure_endpoint=endpoint,
            api_key=os.getenv("AZURE_OPENAI_API_KEY")
        )
        
        # Get investment profile through conversation
        print("\n💬 Starting conversation to gather investment preferences...")
        profile = get_investment_profile(client)
        print("\nInvestment Profile:")
        print(profile)
        
        # Parse the profile
        user_data = json.loads(profile)
        
        # Convert sector_preference to sectors if needed
        if "sector_preference" in user_data:
            user_data["sectors"] = user_data.pop("sector_preference")
        
        # Define sample tickers (you might want to make this dynamic based on user preferences)
        sample_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
        
        # Analyze stocks
        analyses = analyze_stocks(sample_tickers, user_data)
        
        # Generate portfolio
        portfolio = generate_portfolio(sample_tickers, analyses, user_data)
        
        # Display results
        print("\n📈 Portfolio Recommendation:")
        print(json.dumps(portfolio, indent=2))
        
    except Exception as e:
        print("\n❌ An error occurred:")
        print(str(e))

if __name__ == "__main__":
    main() 