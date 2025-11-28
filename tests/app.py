import streamlit as st
from langchain_openai import AzureChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from portfolio_logic import generate_portfolio
import json
import re
from langchain.schema.messages import AIMessage
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def extract_profile_from_summary(summary_text):
    parser_llm = AzureChatOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version="2024-02-15-preview",
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        temperature=0.2
    )
    
    parser_prompt = """
    You are a JSON extraction assistant. Your task is to extract specific fields from the input text and return them as a JSON object.

    REQUIRED OUTPUT FORMAT:
    {
      "risk_tolerance": "conservative" | "moderate" | "aggressive",
      "investment_horizon": "short_term" | "medium_term" | "long_term",
      "sector_preference": ["technology" | "healthcare" | "green_energy" | "finance" | "no_preference"]
    }

    FIELD RULES:
    1. risk_tolerance: Must be exactly one of: "conservative", "moderate", "aggressive"
    2. investment_horizon: Must be exactly one of: "short_term", "medium_term", "long_term"
    3. sector_preference: Must be an array containing one or more of: "technology", "healthcare", "green_energy", "finance", "no_preference"

    EXAMPLES:
    Valid response:
    {
      "risk_tolerance": "moderate",
      "investment_horizon": "long_term",
      "sector_preference": ["technology", "finance"]
    }

    Invalid responses:
    []  // Empty array is not valid
    {}  // Empty object is not valid
    {"risk_tolerance": "moderate"}  // Missing required fields

    IMPORTANT:
    - You MUST return a complete JSON object with ALL three required fields
    - The response must start with { and end with }
    - Do not include any additional text or formatting
    - Do not return an empty array or object

    Input text to analyze:
    """ + summary_text

    response = parser_llm.invoke([HumanMessage(content=parser_prompt)]).content
    print("\n=== Parser Response ===")
    print(response)
    print("=====================\n")
    
    # Clean and validate the response
    clean_json = re.sub(r"```json|```", "", response).strip()
    if not clean_json:
        raise ValueError("Parser returned empty response")
    
    # Ensure the response starts with { and ends with }
    if not clean_json.startswith("{") or not clean_json.endswith("}"):
        # Try to fix common issues
        if clean_json.startswith('"') and clean_json.endswith('"'):
            clean_json = clean_json[1:-1]  # Remove quotes
        if not clean_json.startswith("{"):
            clean_json = "{" + clean_json
        if not clean_json.endswith("}"):
            clean_json = clean_json + "}"
    
    # Validate that it's not an empty array or object
    if clean_json in ["[]", "{}"]:
        raise ValueError("Parser returned empty array or object")
    
    return clean_json

st.set_page_config(page_title="Bionic Advisor", page_icon="📊")
st.title("📊 Bionic Advisor")

if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content=("""
You are a financial assistant. Your job is to collect three user preferences and return them as JSON.

The response MUST be a valid JSON object with these exact fields:
{
  "risk_tolerance": "conservative" | "moderate" | "aggressive",
  "investment_horizon": "short_term" | "medium_term" | "long_term",
  "sector_preference": ["technology" | "healthcare" | "green_energy" | "finance" | "no_preference"]
}

Guidelines:
1. risk_tolerance: "conservative", "moderate", or "aggressive"
   - e.g., "risky" = aggressive, "safe" = conservative

2. investment_horizon: "short_term", "medium_term", or "long_term"
   - e.g., 2 years = short_term, 10+ years = long_term

3. sector_preference: one or more of:
   - "technology", "healthcare", "green_energy", "finance", "no_preference"

Ask one question at a time. After each answer:
- Confirm what was captured in plain text
- Show the current profile so far
- Then ask the next question

If the user provides all 3 at once, skip to final step.

⚠️ Once all 3 fields are filled, reply with ONLY the JSON object, nothing else.
Do not include any markdown formatting, no ```json``` tags, just the raw JSON.
  """))
    ]

# Chat-like conversation display and input
st.subheader("💬 Chat")
with st.container():
    for msg in st.session_state.messages[1:]:  # Skip system message
        if isinstance(msg, HumanMessage):
            with st.chat_message("user"):
                st.markdown(msg.content)
        else:
            with st.chat_message("assistant"):
                st.markdown(msg.content)

    # Scroll anchor for reliable autoscroll to latest message
    scroll_target = st.empty()
    scroll_target.markdown("<div id='scroll-anchor'></div>", unsafe_allow_html=True)

    st.markdown("""
        <script>
            const anchor = document.getElementById("scroll-anchor");
            if (anchor) {
                anchor.scrollIntoView({ behavior: "smooth" });
            }
        </script>
    """, unsafe_allow_html=True)

    # Input directly under messages
    with st.form("portfolio_form", clear_on_submit=True):
        user_input = st.text_input("Your message:", key="user_input_field")
        submitted = st.form_submit_button("Send")

# Initialize the main LLM
llm = AzureChatOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version="2024-02-15-preview",
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    temperature=0.7
)

if submitted and user_input:
    user_msg = HumanMessage(content=user_input)
    st.session_state.messages.append(user_msg)

    with st.spinner("💬 Thinking..."):
        response = llm(st.session_state.messages)
        print("\n=== Raw LLM Response ===")
        print(response.content)
        print("======================\n")

    st.session_state.messages.append(response)

    # Try to extract JSON and trigger engine if complete
    try:
        # First try to parse the response directly as JSON
        try:
            print("\n=== Attempting direct JSON parse ===")
            print("Raw response content:")
            print(response.content)
            user_data = json.loads(response.content)
            print("Direct parse successful!")
            # Store user_data immediately once parsed successfully
            st.session_state.user_data = user_data
        except json.JSONDecodeError as e:
            print(f"Direct parse failed: {str(e)}")
            # If direct parsing fails, try to extract JSON using the parser
            print("\n=== Attempting parser extraction ===")
            parsed = extract_profile_from_summary(response.content)
            st.info("🧠 Extracting structured profile from assistant response...")
            st.code(response.content, language="markdown")
            st.markdown("🔍 Parsing result:")
            st.code(parsed, language="json")
            print("\n---- Assistant Output ----\n", response.content)
            print("\n---- Parser Output ----\n", parsed)
            clean_json = re.sub(r"```json|```", "", parsed).strip()
            print("\n=== Cleaned JSON ===")
            print(clean_json)
            print("===================\n")

            # Fix single quotes to double quotes if JSON appears malformed
            if clean_json.startswith("{") and "'" in clean_json and '"' not in clean_json:
                clean_json = clean_json.replace("'", '"')
                print("🔧 Converted single quotes to double quotes in JSON")

            # Also add this for visibility before parsing:
            print("Cleaned for JSON parsing:")
            print(clean_json)

            # Insert check before json.loads
            if not clean_json:
                raise ValueError("Parser returned empty response")
            if not clean_json.startswith("{"):
                raise ValueError(f"Parser returned invalid JSON format. Got: {clean_json[:100]}...")

            user_data = json.loads(clean_json)
            # Store user_data immediately once parsed successfully
            st.session_state.user_data = user_data

        # Validate required fields
        required_keys = {"risk_tolerance", "investment_horizon", "sector_preference"}
        if not required_keys.issubset(user_data.keys()):
            raise ValueError(f"Missing required fields. Got: {list(user_data.keys())}, Need: {list(required_keys)}")

        # Convert sector_preference to sectors if needed
        if "sector_preference" in user_data:
            user_data["sectors"] = user_data.pop("sector_preference")

        st.session_state.portfolio_result = generate_portfolio(user_data)
    except Exception as e:
        st.session_state.portfolio_error = str(e)
        print(f"\n=== Error Details ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"Response content: {response.content}")
        print("===================\n")

    st.rerun()

# After form: display result if available
if "user_data" in st.session_state:
    st.success("✅ Structured input parsed.")

    # Display investment profile
    st.subheader("📋 Investment Profile")
    st.json(st.session_state.user_data)

    # Display portfolio recommendation if available
    if "portfolio_result" in st.session_state:
        st.subheader("📈 Portfolio Recommendation")
        st.json(st.session_state.portfolio_result)
elif "portfolio_error" in st.session_state:
    st.error(f"❌ Failed to parse JSON: {st.session_state.portfolio_error}")