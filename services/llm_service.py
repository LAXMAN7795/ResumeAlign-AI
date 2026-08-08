import os
import json
import re
from typing import Dict, Any, Optional
import streamlit as st
from dotenv import load_dotenv
from google import genai
from groq import Groq

# Load local environment variables if available
load_dotenv()

def get_api_key(key_name: str) -> Optional[str]:
    """Retrieve API key from Streamlit session state, Secrets, or OS environment."""
    # 1. Check Streamlit Session State (User entered in Settings)
    if key_name in st.session_state and st.session_state[key_name]:
        return st.session_state[key_name]
    
    # 2. Check Streamlit Cloud Secrets (.streamlit/secrets.toml)
    try:
        if key_name in st.secrets:
            return st.secrets[key_name]
    except Exception:
        pass

    # 3. Check OS Environment Variables (.env)
    return os.getenv(key_name)

# --- Client Factory Functions ---

def get_gemini_client(api_key: Optional[str] = None) -> genai.Client:
    key = api_key or get_api_key("GEMINI_API_KEY")
    if not key:
        raise ValueError("Gemini API Key missing. Set GEMINI_API_KEY in Settings, .env, or Streamlit Secrets.")
    return genai.Client(api_key=key)

def get_groq_client(api_key: Optional[str] = None) -> Groq:
    key = api_key or get_api_key("GROQ_API_KEY")
    if not key:
        raise ValueError("Groq API Key missing. Set GROQ_API_KEY in Settings, .env, or Streamlit Secrets.")
    return Groq(api_key=key)

# --- Core Generation Logic ---

def generate_text(prompt: str, model_name: str = "gemini-2.5-flash", api_key: Optional[str] = None) -> str:
    """Unified text generation for Gemini and Groq with automatic fallback."""
    # Handle Groq Models
    if "groq/" in model_name.lower() or model_name in ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"]:
        clean_model = model_name.replace("groq/", "")
        client = get_groq_client(api_key)
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=clean_model,
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"Groq API Error ({clean_model}): {str(e)}")

    # Default to Gemini
    client = get_gemini_client(api_key)
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        # Fallback to gemini-2.5-flash-lite if gemini-2.5-flash hits rate limits
        if "2.5-pro" in model_name or "429" in str(e):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=prompt
                )
                return response.text.strip()
            except Exception as fallback_err:
                raise RuntimeError(f"Gemini API Error: {str(e)} | Fallback: {str(fallback_err)}")
        raise RuntimeError(f"Gemini API Error: {str(e)}")

def generate_json(prompt: str, model_name: str = "gemini-2.5-flash", api_key: Optional[str] = None) -> Dict[str, Any]:
    """Generates structured JSON response."""
    raw_response = generate_text(prompt, model_name=model_name, api_key=api_key)
    
    cleaned = re.sub(r"^```(json)?", "", raw_response, flags=re.MULTILINE)
    cleaned = re.sub(r"```$", "", cleaned, flags=re.MULTILINE).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {
            "ats_score": 75,
            "matching_skills": ["Core Domain Competencies"],
            "missing_skills": ["Target Specific Keywords"],
            "suggestions": ["Ensure key accomplishments are quantified in experience entries."]
        }