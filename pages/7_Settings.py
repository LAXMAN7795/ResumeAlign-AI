import streamlit as st

st.title("⚙️ Application Settings")
st.caption("Manage API key configurations, LLM providers, and export preferences.")

st.subheader("1. API Key Configurations")
st.info("Keys provided here override environment variables for the active session.")

gemini_key_input = st.text_input(
    "Google Gemini API Key",
    value=st.session_state.get("GEMINI_API_KEY", ""),
    type="password",
    placeholder="AIzaSy..."
)

groq_key_input = st.text_input(
    "Groq API Key (Optional)",
    value=st.session_state.get("GROQ_API_KEY", ""),
    type="password",
    placeholder="gsk_..."
)

if st.button("💾 Save Key Configurations", type="primary"):
    st.session_state["GEMINI_API_KEY"] = gemini_key_input.strip()
    st.session_state["GROQ_API_KEY"] = groq_key_input.strip()
    st.success("API Key settings updated for active session!")

st.divider()

st.subheader("2. Streamlit Cloud Secrets Template")
st.caption("If deploying to Streamlit Cloud, add the following snippet to your app's Secrets setting:")

st.code("""
# Inside Streamlit Cloud -> App Settings -> Secrets
GEMINI_API_KEY = "your_actual_gemini_api_key_here"
GROQ_API_KEY = "your_actual_groq_api_key_here"
""", language="toml")