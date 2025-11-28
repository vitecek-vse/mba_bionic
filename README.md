# mba_bionic
SHORT VERSION 
Hybrid AI Advisor — A modular multi-agent system for personalized wealth management. Combines GPT-based client profiling, rule-based portfolio selection, market-signal analytics, and a deterministic Python rebalancing engine, with dual validation for transparent, auditable recommendations.
FULL VERSION
**Hybrid AI Advisor – Multi-Agent Wealth-Management Platform**

A next-generation modular advisory system built for personalized, transparent, and scalable investment guidance.

📌 Overview

This project implements a Hybrid AI Advisor, developed as part of an MBA thesis focused on next-generation wealth-management technology.
The system combines LLM-driven client interaction, deterministic portfolio logic, and a Python-based rebalancing engine, orchestrated through a multi-agent architecture designed for transparency, auditability, and ease of integration.

The goal is to demonstrate a credible, scalable model for “one-client–one-AI-advisor” workflows within modern financial institutions.

🧠 System Architecture

The platform consists of several coordinated modules:

1. Conversational AI Agent

Built on GPT-based models

Extracts structured risk profile, investment goals, constraints

Produces deterministic JSON responses for downstream processing

2. AI Portfolio Selector

Rule-based investment strategy mapping

Deterministic and auditable decision paths

Supports risk buckets, horizons, diversification rules

3. Market Signal Engine

Incorporates professional indicators:

Squeeze Momentum Indicator (SMI)

Parabolic SAR

Moving averages (20/50/200)

Provides tactical market context for allocations.

4. Python Rebalancing Engine

Deterministic portfolio updates

Position-level diffs (buy/sell)

JSON-formatted transaction instructions

Supports reproducible backtesting and scenario analysis

5. Validation Layer

Ensures reliability and internal consistency:

Cosine-similarity benchmark vs. prior recommendations

Peer-LLM cross-evaluation

Optional human-in-the-loop approval

🚀 Features

Multi-agent orchestration (MANUS-inspired architecture)

Modular design — each component replaceable in isolation

Portable Python backend, notebook-friendly

Deterministic outputs suitable for compliance review

Ready for future integration with Core Banking System providers and trading APIs  or advisory front ends

📁 Project Structure
mba_bionic/
│
├── advisor.py                # Entry point for AI workflow orchestration
├── data/                     # Loaders, metadata, S&P500 lists
├── engine/                   # Portfolio engine, backtests, metrics
├── filter/                   # Screener and market-signal utilities
├── tests/                    # Basic test harness for portfolio logic
├── notebooks/ (optional)     # EDA, prototyping, early modeling
├── .gitignore                # Protects secrets, pycache, DS_Store
└── README.md

🛠 How to Run
1️⃣ Create virtual environment
python3 -m venv venv
source venv/bin/activate

2️⃣ Install dependencies
pip install -r requirements.txt

3️⃣ Add your Azure OpenAI key (local only)

Create file .env.local (never tracked by git):

AZURE_OPENAI_KEY=your_key
AZURE_OPENAI_ENDPOINT=your_endpoint

4️⃣ Run main workflow
python advisor.py

🧪 Testing

Basic test suite:

pytest tests/

🎓 Academic Context

This project is part of the MBA thesis “Hybrid AI Advisor: A Multi-Agent Model for Next-Generation Wealth Management” at the University of Economics in Prague.

The system demonstrates:

scalable augmentation of advisory workflows

automated personalization

transparent reasoning chains for compliance

feasibility of hybrid human–AI advisory models

📜 License

This project is for academic and research purposes only.
Commercial use requires additional permissions.

🤝 Contributions

Contributions, improvements, and extensions are welcome through pull requests.
