import streamlit as st
import pathlib

st.set_page_config(
    page_title="ResumeAlign AI | ATS Optimization",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
css_path = pathlib.Path("assets/css/style.css")
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Main Navigation Dashboard
st.sidebar.title("⚡ ResumeAlign AI")
st.sidebar.caption("SaaS ATS Optimization Platform")
st.sidebar.divider()

st.title("🏠 Executive Dashboard")
st.caption("Welcome back! Here is an overview of your resume optimization workflow.")

# Metrics Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
        <div class="metric-card">
            <h3>Candidate Profile</h3>
            <div class="metric-value">Active</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="metric-card">
            <h3>Target JDs Saved</h3>
            <div class="metric-value">3</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="metric-card">
            <h3>Average ATS Score</h3>
            <div class="metric-value">87%</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
        <div class="metric-card">
            <h3>Resumes Generated</h3>
            <div class="metric-value">12</div>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# Quick Workflow Guide
st.subheader("⚡ Recommended Optimization Workflow")
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("### 1. Fill Profile")
    st.info("Enter your true experiences, skills, and projects in **Candidate Profile**.")

with c2:
    st.markdown("### 2. Add Target Job")
    st.info("Paste the target job description in **Job Description**.")

with c3:
    st.markdown("### 3. Generate & Analyze")
    st.info("Run the AI pipeline to tailor your resume and boost your ATS score.")