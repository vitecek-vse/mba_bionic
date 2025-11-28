import streamlit as st
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import json
from data.sp500_loader import get_sp500_tickers, get_stock_metadata, update_sp500_metadata
import pandas as pd
from agents.fundamental_agent import FundamentalAgent
from agents.portfolio_manager import PortfolioManager

# Set page config must be the first Streamlit command
st.set_page_config(page_title="Bionic Advisor Demo", layout="wide")

# Initialize stock metadata if not exists and load into session state
metadata_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/stock_metadata.csv")
if 'stock_metadata_df' not in st.session_state:
    if not os.path.exists(metadata_path):
        with st.spinner("Initializing stock metadata..."):
            update_sp500_metadata()
    st.session_state.stock_metadata_df = pd.read_csv(metadata_path)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'preferences' not in st.session_state:
    st.session_state.preferences = {
        'risk_tolerance': None,
        'investment_horizon': None,
        'sectors': None
    }
if 'chat_focus' not in st.session_state:
    st.session_state.chat_focus = None
if 'chat_focus_active' not in st.session_state:
    st.session_state.chat_focus_active = None
if 'debug_mode' not in st.session_state:
    st.session_state.debug_mode = False

# Initialize Azure OpenAI client
load_dotenv()
client = AzureOpenAI(
    api_version="2024-12-01-preview",
    azure_endpoint="https://bionicadvisor.openai.azure.com/",
    api_key=os.getenv("AZURE_OPENAI_API_KEY")
)

# Simple progress tracker
def get_progress():
    prefs = st.session_state.preferences
    return {
        'risk': bool(prefs['risk_tolerance']),
        'horizon': bool(prefs['investment_horizon']),
        'sectors': bool(prefs['sectors'])
    }

# Display progress
def show_progress():
    progress = get_progress()
    st.markdown("### Progress")
    st.markdown(f"""
    - Risk Tolerance: {'✅' if progress['risk'] else '⭕️'}
    - Investment Horizon: {'✅' if progress['horizon'] else '⭕️'}
    - Preferred Sectors: {'✅' if progress['sectors'] else '⭕️'}
    """)

# Main UI
st.title("🤖 Investment Advisor Chat")

# Add tooltips and styling
st.markdown('''
    <style>
    .tooltip {
        position: relative;
        display: inline-block;
    }
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    .checkmark-anim {
        display: inline-block;
        animation: fadeIn 0.5s;
    }
    @keyframes fadeIn {
        0% { opacity: 0; }
        100% { opacity: 1; }
    }
    </style>''', unsafe_allow_html=True)





# Display chat history
for message in st.session_state.chat_history:
    if message['role'] == 'user':
        st.markdown(f"**You:** {message['content']}")
    else:
        st.markdown(f"**Advisor:** {message['content']}")


# Add a button to proceed to portfolio generation if all preferences are collected
if all(st.session_state.preferences.values()):
    if st.button("Generate Portfolioo", key="portfolio_btn"):
        st.markdown("### Portfolio Generation")
        st.info("This is where we would generate the portfolio based on the collected preferences.")
        # Here you would add the portfolio generation logic

# --- Helper functions (reuse your logic) ---
def get_investment_profile(client, risk, horizon, sectors):
    system_prompt = f"""You are a financial advisor assistant. Create an investment profile based on the following preferences:
- Risk tolerance: {risk}
- Investment horizon: {horizon}
- Preferred sectors: {', '.join(sectors)}

Return the profile as a JSON object with these exact fields:
{{
    \"risk_tolerance\": \"{risk}\",
    \"investment_horizon\": \"{horizon}\",
    \"sectors\": {json.dumps(sectors)}
}}"""
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Create an investment profile."}
        ],
        max_tokens=4096,
        temperature=0.7,
        model="gpt-35-turbo"
    )
    return response.choices[0].message.content

def analyze_stocks(tickers, context):
    fundamental_agent = FundamentalAgent()
    analyses = {}
    for ticker in tickers:
        analyses[ticker] = fundamental_agent.analyze(ticker, context)
    return analyses

def generate_portfolio(tickers, analyses, context):
    portfolio_manager = PortfolioManager()
    return portfolio_manager.analyze(tickers, analyses, context)

# --- Streamlit UI ---

# Add reset button at the top
if st.button("🔄 Reset Everything", type="primary", help="Clear all data and start fresh"):
    # Clear all session state variables
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()



# --- Step-by-Step Manual ---
st.markdown("""
## How to Use the Bionic Advisor App

**STEP 1: Chat with the Advisor**
- Use the chat window on the left to discuss your investment goals, risk awareness, and preferences with the AI advisor.
- The AI will help you clarify your risk profile and other preferences.

**STEP 2: Enter/Review Your Investment Preferences**
- The app will use the chat to pre-fill your risk awareness and preferences.
- You can review and adjust them in the main form below.
- Click **Submit Preferences** to save your choices.

**STEP 3: Generate Your Portfolio**
- Click **Generate Portfolio** to start the analysis and portfolio generation process.

**STEP 4: View Results**
- Use the tabs below to view your investment profile, stock analyses, and portfolio recommendation (with a pie chart and risk summary).

---
- You can change your preferences at any time and re-generate the portfolio.
- The app analyzes up to 10 stocks at a time to avoid API rate limits.
- The maximum weight for any single stock in your portfolio is capped at 4%.
""")

# --- Layout: Chat on the left, main form on the right ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Step 1: Chat with the Advisor")
    load_dotenv()
    endpoint = "https://bionicadvisor.openai.azure.com/"
    api_version = "2024-12-01-preview"
    client = AzureOpenAI(
        api_version=api_version,
        azure_endpoint=endpoint,
        api_key=os.getenv("AZURE_OPENAI_API_KEY")
    )
    # Chat state
    if 'guided_chat' not in st.session_state:
        st.session_state['guided_chat'] = {
            'messages': [
                {"role": "system", "content": """You are a financial advisor assistant. Your task is to help users determine their investment preferences.
                You need to collect:
                1. Risk tolerance (low, moderate, high)
                2. Investment horizon (short_term, medium_term, long_term)
                3. Preferred sectors (from: Technology, Healthcare, Financials, Energy, Consumer Discretionary, Consumer Staples, Industrials, Materials, Utilities, Real Estate, Communication Services)
                
                Have a natural conversation with the user to collect these preferences. After EACH response, include a JSON object showing your current understanding of their preferences. Format your response like this:
                
                [Your natural conversation response here]
                
                <preferences>
                {
                    "risk_tolerance": "low/moderate/high or null if not yet determined",
                    "investment_horizon": "short_term/medium_term/long_term or null if not yet determined",
                    "sectors": ["sector1", "sector2", ...] or [] if not yet determined
                }
                </preferences>
                
                Keep the conversation natural, but always include the preferences JSON at the end of your response, even if some preferences are still null or empty."""}
            ],
            'preferences': None
        }
    guided = st.session_state['guided_chat']
    
    # Show chat history
    for msg in guided['messages']:
        if msg['role'] == 'user':
            st.markdown(f"**You:** {msg['content']}")
        elif msg['role'] == 'assistant':
            # Split the response to separate conversation from preferences JSON
            content = msg['content']
            if '<preferences>' in content:
                conversation, preferences_json = content.split('<preferences>')
                st.markdown(f"**Advisor:** {conversation.strip()}")
                if st.session_state.debug_mode:
                    try:
                        # Clean up the JSON string by removing any extra content after the closing brace
                        json_str = preferences_json.strip()
                        if '}' in json_str:
                            json_str = json_str[:json_str.rindex('}')+1]
                        preferences = json.loads(json_str)
                        st.json(preferences)
                    except json.JSONDecodeError as e:
                        st.error(f"Error parsing preferences JSON: {str(e)}")
                        st.code(preferences_json.strip(), language="text")
                try:
                    # Use the same cleaned JSON for updating preferences
                    if '}' in preferences_json:
                        json_str = preferences_json[:preferences_json.rindex('}')+1]
                        preferences = json.loads(json_str)
                        if preferences and any(preferences.values()):
                            guided['preferences'] = preferences
                except json.JSONDecodeError:
                    pass
            else:
                st.markdown(f"**Advisor:** {content}")
    
    # User input using a form
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("You:", key="guided_chat_input")
        submitted = st.form_submit_button("Send")
        
        if submitted and user_input:
            # Add user message to history
            guided['messages'].append({'role': 'user', 'content': user_input})
            
            # Get response from Azure API
            response = client.chat.completions.create(
                messages=guided['messages'],
                max_tokens=4096,
                temperature=0.7,
                model="gpt-35-turbo"
            )
            
            # Get AI response
            ai_response = response.choices[0].message.content
            
            # Add AI response to history
            guided['messages'].append({'role': 'assistant', 'content': ai_response})
            
            # Parse preferences from the response if it contains the <preferences> tag
            if '<preferences>' in ai_response:
                conversation, preferences_json = ai_response.split('<preferences>')
                try:
                    preferences = json.loads(preferences_json.strip())
                    if preferences and any(preferences.values()):
                        guided['preferences'] = preferences
                        st.session_state['guided_chat'] = guided
                except json.JSONDecodeError:
                    pass
            
            st.rerun()  # Rerun to update the chat history and button states immediately

    # Show current values if we have them
    if guided['preferences']:
        st.markdown("**Current Values:**")
        st.markdown(f"- Risk Tolerance: {guided['preferences']['risk_tolerance']}")
        st.markdown(f"- Investment Horizon: {guided['preferences']['investment_horizon']}")
        st.markdown(f"- Preferred Sectors: {', '.join(guided['preferences']['sectors'])}")

    # --- Show current values for each topic ---
    st.markdown('''<style>
    .checkmark-anim {
        display: inline-block;
        animation: pop 0.4s ease;
        color: #28a745;
        font-size: 1.2em;
        margin-left: 0.3em;
    }
    @keyframes pop {
        0% { transform: scale(0.2); opacity: 0; }
        70% { transform: scale(1.2); opacity: 1; }
        100% { transform: scale(1); opacity: 1; }
    }
    </style>''', unsafe_allow_html=True)


    # --- Step 1 Buttons for Chat Focus ---
    st.markdown('''<style>
    .step-btn:hover {
        background-color: #218838 !important;
        color: white !important;
        cursor: pointer;
    }
    .step2-highlight {
        border: 3px solid #28a745 !important;
        border-radius: 8px;
        box-shadow: 0 0 10px #28a74544;
        animation: fadeBorder 2s forwards;
    }
    @keyframes fadeBorder {
        0% { border-color: #28a745; }
        80% { border-color: #28a745; }
        100% { border-color: transparent; }
    }
    .tooltip {
        display: inline-block;
        position: relative;
        border-bottom: 1px dotted #888;
        cursor: help;
    }
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 220px;
        background-color: #222;
        color: #fff;
        text-align: left;
        border-radius: 6px;
        padding: 8px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -110px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 0.95em;
    }
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    </style>''', unsafe_allow_html=True)
    
    # Debug output
    if st.session_state.debug_mode:
        st.markdown("---")
        st.markdown("**Debug - Current Preferences State:**")
        st.json(guided.get('preferences', {}))
        st.markdown("---")
    
    active_focus = st.session_state.get('chat_focus_active', None)
    col_risk, col_horizon, col_sector = st.columns(3)
    
    # Get current preferences from guided chat
    current_prefs = guided.get('preferences', {}) or {}
    
    with col_risk:
        st.markdown('<div class="tooltip">', unsafe_allow_html=True)
        risk_value = current_prefs.get('risk_tolerance')
        if risk_value and risk_value not in [None, '']:
            button_color = '#28a745'  # Green for set
            button_text = f'RISK TOLERANCE: {risk_value.upper()} ✓'
        else:
            button_color = '#6c757d'  # Gray for not set
            button_text = 'RISK TOLERANCE'
        
        st.markdown(f'<button class="step-btn" style="background-color:{button_color};color:white;font-weight:bold;width:100%;border:none;padding:0.5em 0.2em;border-radius:4px;">{button_text}</button>', unsafe_allow_html=True)
        if st.button('Edit Risk Tolerance', key='edit_risk_btn_1'):
            st.session_state['chat_focus'] = 'risk_tolerance'
            st.session_state['chat_focus_active'] = 'risk_tolerance'
        st.markdown('<span class="tooltiptext">How much risk are you willing to take? Low = safer, High = more potential reward but more risk.</span></div>', unsafe_allow_html=True)
        if active_focus == 'risk_tolerance':
            st.markdown('<span style="color:#FFD700;font-weight:bold;">Active</span>', unsafe_allow_html=True)
    
    with col_horizon:
        st.markdown('<div class="tooltip">', unsafe_allow_html=True)
        horizon_value = current_prefs.get('investment_horizon')
        if horizon_value and horizon_value not in [None, '']:
            button_color = '#28a745'  # Green for set
            button_text = f'INVESTMENT HORIZON: {horizon_value.upper()} ✓'
        else:
            button_color = '#6c757d'  # Gray for not set
            button_text = 'INVESTMENT HORIZON'
        
        st.markdown(f'<button class="step-btn" style="background-color:{button_color};color:white;font-weight:bold;width:100%;border:none;padding:0.5em 0.2em;border-radius:4px;">{button_text}</button>', unsafe_allow_html=True)
        if st.button('Edit Investment Horizon', key='edit_horizon_btn_1'):
            st.session_state['chat_focus'] = 'investment_horizon'
            st.session_state['chat_focus_active'] = 'investment_horizon'
        st.markdown('<span class="tooltiptext">How long do you plan to invest? Short = <3 years, Medium = 3-7 years, Long = 7+ years.</span></div>', unsafe_allow_html=True)
        if active_focus == 'investment_horizon':
            st.markdown('<span style="color:#FFD700;font-weight:bold;">Active</span>', unsafe_allow_html=True)
    
    with col_sector:
        st.markdown('<div class="tooltip">', unsafe_allow_html=True)
        sectors = current_prefs.get('sectors', [])
        if sectors and len(sectors) > 0:
            button_color = '#28a745'  # Green for set
            button_text = f'PREFERRED SECTORS: {len(sectors)} SELECTED ✓'
        else:
            button_color = '#6c757d'  # Gray for not set
            button_text = 'PREFERRED SECTORS'
        
        st.markdown(f'<button class="step-btn" style="background-color:{button_color};color:white;font-weight:bold;width:100%;border:none;padding:0.5em 0.2em;border-radius:4px;">{button_text}</button>', unsafe_allow_html=True)
        if st.button('Edit Preferred Sector', key='edit_sector_btn_1'):
            st.session_state['chat_focus'] = 'sectors'
            st.session_state['chat_focus_active'] = 'sectors'
        st.markdown('<span class="tooltiptext">Which industries are you most interested in for your investments?</span></div>', unsafe_allow_html=True)
        if active_focus == 'sectors':
            st.markdown('<span style="color:#FFD700;font-weight:bold;">Active</span>', unsafe_allow_html=True)

    # --- Proceed to Step 2 Button ---
    if guided['preferences']:
        if st.button('Proceed to Step 2', key='proceed_step2'):
            st.session_state['risk'] = guided['preferences']['risk_tolerance']
            st.session_state['horizon'] = guided['preferences']['investment_horizon']
            st.session_state['sectors'] = guided['preferences']['sectors']
            st.session_state['step2_highlight'] = True
            try:
                st.toast('Step 1 complete! Proceed to Step 2 to review and submit your preferences.', icon='✅')
            except Exception:
                st.success('Step 1 complete! Proceed to Step 2 to review and submit your preferences.')
            st.rerun()



with col2:
    # --- Collect preferences from client via a form ---
    highlight = st.session_state.pop('step2_highlight', False)
    if highlight:
        st.markdown('<div class="step2-highlight">', unsafe_allow_html=True)
    st.header("Step 2: Enter Your Investment Preferences")
    st.caption("Fill in or review your preferences. Hover over each field for more info.")
    risk_options = ["low", "moderate", "high"]
    default_risk = st.session_state.get('risk', 'moderate')
    if default_risk not in risk_options:
        default_risk = "moderate"
    sector_options = [
        'Technology', 'Healthcare', 'Financials', 'Energy', 'Consumer Discretionary',
        'Consumer Staples', 'Industrials', 'Materials', 'Utilities', 'Real Estate', 'Communication Services'
    ]
    default_sectors = st.session_state.get('sectors', ['Technology', 'Healthcare'])
    default_horizon = st.session_state.get('horizon', 'medium_term')
    with st.form("client_preferences"):
        form_risk = st.selectbox(
            "Risk Tolerance",
            risk_options,
            index=risk_options.index(default_risk),
            key="form_risk",
            help="How much risk are you willing to take? Low = safer, High = more potential reward but more risk."
        )
        form_horizon = st.selectbox(
            "Investment Horizon",
            ["short_term", "medium_term", "long_term"],
            index=["short_term", "medium_term", "long_term"].index(default_horizon),
            key="form_horizon",
            help="How long do you plan to invest? Short = <3 years, Medium = 3-7 years, Long = 7+ years."
        )
        form_sectors = st.multiselect(
            "Preferred Sectors",
            sector_options,
            default=default_sectors,
            key="form_sectors",
            help="Which industries are you most interested in for your investments?"
        )

        # Filter tickers by selected sector(s)
        metadata = st.session_state.stock_metadata_df
        filtered_tickers = metadata[
            metadata["sector"].isin(form_sectors) & (metadata["sector"] != "Unknown")
        ]["ticker"].unique().tolist()
        filtered_tickers_str = ", ".join(filtered_tickers)

        # Show filtered tickers as a read-only summary
        st.markdown("**Stocks matching your sector selection:**")
        st.code(filtered_tickers_str, language=None)
        st.caption("These stocks will be used for your portfolio analysis.")

        submitted = st.form_submit_button("Submit Preferences")

    if submitted:
        st.session_state['risk'] = form_risk
        st.session_state['horizon'] = form_horizon
        st.session_state['sectors'] = form_sectors
        st.session_state['tickers'] = filtered_tickers_str
        st.success("Preferences submitted! Now click 'Generate Portfolio' below.")
        #st.rerun()  # Force rerun to update progress bar

    # --- Main Page Tabs ---
    tabs = st.tabs(["Investment Profile", "Stock Analyses", "Portfolio Recommendation"])

    if st.button("Generate Portfolio", key="run_portfolio"):
        risk = st.session_state.get('risk', default_risk)
        horizon = st.session_state.get('horizon', 'medium_term')
        sectors = st.session_state.get('sectors', ['technology', 'healthcare'])
        tickers = st.session_state.get('tickers', ",".join(get_sp500_tickers()))
        with st.spinner("Generating investment profile..."):
            profile = get_investment_profile(client, risk, horizon, sectors)
            profile_dict = json.loads(profile)
            st.session_state.profile = profile_dict  # Store profile in session state
        with st.spinner("Analyzing stocks..."):
            ticker_list = [t.strip().upper() for t in tickers.split(",") if t.strip()]
            ticker_list = ticker_list[:30]
            if st.session_state.debug_mode:
                st.write(f"Tickers passed to analyze_stocks and generate_portfolio: {ticker_list}")
            analyses = analyze_stocks(ticker_list, profile_dict)
            st.session_state.analyses = analyses  # Store analyses in session state
        with st.spinner("Generating portfolio..."):
            portfolio = generate_portfolio(ticker_list, analyses, profile_dict)
            st.session_state.portfolio = portfolio  # Store portfolio in session state
            st.rerun()  # Force rerun to update progress bar

    # Show results in tabs
    with tabs[0]:
        st.subheader("Investment Profile")
        if 'profile' in st.session_state:
            st.json(st.session_state.profile)
    
    with tabs[1]:
        st.subheader("Stock Analyses")
        if 'analyses' in st.session_state:
            st.json(st.session_state.analyses)
    
    with tabs[2]:
        st.subheader("Portfolio Recommendation")
        if 'portfolio' in st.session_state:
            portfolio = st.session_state.portfolio
            if "portfolio" in portfolio:
                import pandas as pd
                import matplotlib.pyplot as plt

                df = pd.DataFrame(portfolio["portfolio"])
                tickers = df["ticker"].tolist()
                weights = df["weight"].tolist()

                # Show tickers as a list
                st.markdown("**Tickers in Portfolio:**")
                st.write(", ".join(tickers))

                # --- Portfolio Table ---
                st.markdown("**Portfolio Details:**")
                portfolio_data = []
                for row in portfolio["portfolio"]:
                    # Retrieve metadata from the already loaded DataFrame in session state
                    metadata = st.session_state.stock_metadata_df
                    meta_row = metadata[metadata['ticker'] == row['ticker']]

                    if st.session_state.debug_mode:
                        st.write(f"Looking up ticker: {row['ticker']}. Found in metadata: {not meta_row.empty}")

                    if not meta_row.empty:
                        meta = meta_row.iloc[0].to_dict()
                    else:
                        meta = None

                    if meta is None:
                        meta = {
                            "name": "N/A",
                            "sector": "N/A",
                            "industry": "N/A"
                        }
                    portfolio_data.append({
                        "Ticker": row["ticker"],
                        "Full Name": meta.get("name", "N/A"),
                        "Sector": meta.get("sector", "N/A"),
                        "Industry": meta.get("industry", "N/A"),
                        "Weight (%)": f"{row['weight']*100:.2f}%"
                    })
                df_table = pd.DataFrame(portfolio_data)
                st.dataframe(df_table, use_container_width=True)

                # Pie chart
                fig, ax = plt.subplots()
                ax.pie(weights, labels=tickers, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')
                st.pyplot(fig)

                # Summarize key risks using GPT if available
                if "key_risks" in portfolio and portfolio["key_risks"]:
                    risks_text = "\n".join(portfolio["key_risks"])
                    gpt_prompt = (
                        "Summarize these key risks in 5 sentences for a portfolio report:\n"
                        f"{risks_text}"
                    )
                    response = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": "You are a financial analyst."},
                            {"role": "user", "content": gpt_prompt}
                        ],
                        max_tokens=512,
                        temperature=0.7,
                        model="gpt-35-turbo"
                    )
                    summary = response.choices[0].message.content
                    st.markdown("**Key Risks (Summary):**")
                    st.write(summary)
            else:
                st.info("No portfolio data to display.")

    if highlight:
        st.markdown('</div>', unsafe_allow_html=True)

# Add test interface in the sidebar
with st.sidebar:
    st.subheader("Test Suite")
    
    # Initialize session state for test results if not exists
    if 'test_results' not in st.session_state:
        st.session_state.test_results = {}
    if 'test_list' not in st.session_state:
        from tests.run_tests import get_test_list
        st.session_state.test_list = get_test_list()
    
    # Test type selection
    test_type = st.radio(
        "Select Test Type",
        ["All Tests", "Unit Tests", "Integration Tests"],
        horizontal=True
    )
    
    # Show test list and status
    st.markdown("### Available Tests")
    
    # Unit Tests Section
    st.markdown("#### Unit Tests")
    for test_name in st.session_state.test_list["unit"]:
        status = st.session_state.test_results.get(test_name, "not_run")
        col1, col2 = st.columns([1, 4])
        with col1:
            if status == "passed":
                st.markdown("✅")
            elif status == "failed":
                st.markdown("❌")
            elif status == "error":
                st.markdown("⚠️")
            else:
                st.markdown("⚪")
        with col2:
            st.markdown(f"`{test_name}`")
    
    # Integration Tests Section
    st.markdown("#### Integration Tests")
    for test_name in st.session_state.test_list["integration"]:
        status = st.session_state.test_results.get(test_name, "not_run")
        col1, col2 = st.columns([1, 4])
        with col1:
            if status == "passed":
                st.markdown("✅")
            elif status == "failed":
                st.markdown("❌")
            elif status == "error":
                st.markdown("⚠️")
            else:
                st.markdown("⚪")
        with col2:
            st.markdown(f"`{test_name}`")
    
    # Run tests button
    if st.button("Run Selected Tests"):
        from tests.run_tests import run_tests
        
        # Map selection to test type
        test_type_map = {
            "All Tests": None,
            "Unit Tests": "unit",
            "Integration Tests": "integration"
        }
        
        with st.spinner("Running tests..."):
            results, logs, test_list = run_tests(test_type_map[test_type])
            
            # Update session state with new results
            for result in results:
                st.session_state.test_results[result.name] = result.status
            
            # Create a container for test results
            test_container = st.container()
            
            # Show test results with checkboxes
            with test_container:
                st.markdown("### Test Results")
                
                # Count passed/failed tests
                passed = sum(1 for r in results if r.status == "passed")
                failed = sum(1 for r in results if r.status in ["failed", "error"])
                
                # Show summary
                st.markdown(f"""
                **Summary:**
                - ✅ Passed: {passed}
                - ❌ Failed: {failed}
                - Total: {len(results)}
                """)
                
                # Show individual test results
                for result in results:
                    with st.expander(f"{'✅' if result.status == 'passed' else '❌'} {result.name}"):
                        # Show test details
                        st.markdown(f"**Status:** {result.status.upper()}")
                        st.markdown(f"**Time:** {result.timestamp.strftime('%H:%M:%S')}")
                        if result.message:
                            st.markdown(f"**Message:** {result.message}")
                        
                        # Show logs in a code block
                        st.markdown("**Logs:**")
                        st.code(result.logs, language="text")
                
                # Show full logs in an expander
                with st.expander("View Full Test Logs"):
                    st.code(logs, language="text")

# Add debug toggle in sidebar
with st.sidebar:
    st.session_state.debug_mode = st.toggle("Debug Mode", value=st.session_state.debug_mode, help="Show JSON preferences in chat") 