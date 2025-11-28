import streamlit as st
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import json
from agents.fundamental_agent import FundamentalAgent
from agents.portfolio_manager import PortfolioManager

# --- Helper functions from run_advisor.py ---
def get_investment_profile(client):
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": """You are a financial advisor assistant. Create an investment profile based on the following preferences:\n- Risk tolerance: moderate\n- Investment horizon: medium_term\n- Preferred sectors: technology, healthcare\n\nReturn the profile as a JSON object with these exact fields:\n{\n    \"risk_tolerance\": \"moderate\",\n    \"investment_horizon\": \"medium_term\",\n    \"sectors\": [\"technology\", \"healthcare\"]\n}"""
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
    fundamental_agent = FundamentalAgent()
    analyses = {}
    for ticker in tickers:
        analysis = fundamental_agent.analyze(ticker, context)
        analyses[ticker] = analysis
    return analyses

def generate_portfolio(tickers: list, analyses: dict, context: dict) -> dict:
    portfolio_manager = PortfolioManager()
    portfolio = portfolio_manager.analyze(tickers, analyses, context)
    return portfolio

# --- Streamlit UI ---
st.set_page_config(page_title="Bionic Advisor", layout="wide")
st.title("🤖 Bionic Advisor")

if 'profile' not in st.session_state:
    st.session_state.profile = None
if 'analyses' not in st.session_state:
    st.session_state.analyses = None
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = None

if st.button("Generate Investment Profile & Portfolio"):
    load_dotenv()
    endpoint = "https://bionicadvisor.openai.azure.com/"
    api_version = "2024-12-01-preview"
    client = AzureOpenAI(
        api_version=api_version,
        azure_endpoint=endpoint,
        api_key=os.getenv("AZURE_OPENAI_API_KEY")
    )
    profile = get_investment_profile(client)
    st.session_state.profile = json.loads(profile)
    sample_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
    analyses = analyze_stocks(sample_tickers, st.session_state.profile)
    st.session_state.analyses = analyses
    portfolio = generate_portfolio(sample_tickers, analyses, st.session_state.profile)
    st.session_state.portfolio = portfolio

if st.session_state.profile:
    st.subheader("Investment Profile")
    st.json(st.session_state.profile)

if st.session_state.analyses:
    st.subheader("Stock Analyses")
    st.json(st.session_state.analyses)

if st.session_state.portfolio:
    st.subheader("Portfolio Recommendation")
    st.json(st.session_state.portfolio) 