import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from database.queries import get_latest_job_description, save_generated_resume
from database.database import init_db
from services.prompt_service import build_analyzer_prompt
from services.llm_service import generate_json

# Ensure database tables exist
init_db()

st.title("📊 ATS Resume Analysis & Visual Breakdown")
st.caption("Evaluate resume-to-job match, uncover missing skills, and get actionable recommendations.")

latest_jd = get_latest_job_description()
current_resume = st.session_state.get("current_generated_resume")

# Guardrails to ensure prerequisite data is available
if not current_resume:
    st.warning("⚠️ No generated resume found in active session! Please generate a resume first.")
    if st.button("👉 Go to Resume Generator"):
        st.switch_page("pages/3_Generate_Resume.py")
    st.stop()

if not latest_jd:
    st.warning("⚠️ No target Job Description found! Please add a job target first.")
    if st.button("👉 Go to Job Description"):
        st.switch_page("pages/2_Job_Description.py")
    st.stop()

st.divider()

# --- Model Selection for Analysis Engine ---
with st.expander("⚙️ Analysis Engine & Model Selection", expanded=False):
    provider = st.radio("Select Provider", ["Google Gemini", "Groq"], horizontal=True, key="analyzer_provider")
    
    if provider == "Google Gemini":
        selected_model = st.selectbox(
            "Select Gemini Model",
            ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.5-pro"],
            index=0,
            key="analyzer_gemini_model",
            help="gemini-2.5-flash provides fast, accurate ATS evaluation."
        )
    else:
        selected_model = st.selectbox(
            "Select Groq Model",
            ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"],
            index=0,
            key="analyzer_groq_model"
        )

# Trigger or Re-Run Analysis Action
run_analysis = st.button("🔄 Run / Re-Run ATS Evaluation", type="primary", use_container_width=True)

if "analysis_results" not in st.session_state or run_analysis:
    with st.spinner("🤖 Running ATS analysis via selected LLM engine..."):
        try:
            prompt = build_analyzer_prompt(current_resume, latest_jd.raw_text)
            results = generate_json(prompt, model_name=selected_model)
            
            st.session_state["analysis_results"] = results
            
            # Save analysis score update if candidate context is present
            if "active_candidate_id" in st.session_state and "active_jd_id" in st.session_state:
                from models.schema import ResumeRecord
                record = ResumeRecord(
                    candidate_id=st.session_state["active_candidate_id"],
                    jd_id=st.session_state["active_jd_id"],
                    generated_markdown=current_resume,
                    ats_score=int(results.get("ats_score", 0))
                )
                save_generated_resume(record)

            st.success("Analysis evaluation complete!")
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")
            st.stop()

# Retrieve analysis output from session state
results = st.session_state.get("analysis_results", {})
ats_score = int(results.get("ats_score", 0))
matching_skills = results.get("matching_skills", [])
missing_skills = results.get("missing_skills", [])
suggestions = results.get("suggestions", [])

st.divider()

# --- Section 1: ATS Score Gauge & Summary Cards ---
col_gauge, col_summary = st.columns([1, 1])

with col_gauge:
    st.subheader("ATS Match Score")
    
    # Custom Plotly Gauge Chart
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=ats_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        number={'suffix': "%", 'font': {'color': "#F8FAFC", 'size': 46}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569"},
            'bar': {'color': "#2563EB"},
            'bgcolor': "#1E293B",
            'borderwidth': 1,
            'bordercolor': "#334155",
            'steps': [
                {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.2)'},
                {'range': [50, 75], 'color': 'rgba(234, 179, 8, 0.2)'},
                {'range': [75, 100], 'color': 'rgba(34, 197, 94, 0.2)'}
            ],
            'threshold': {
                'line': {'color': "#22C55E", 'width': 4},
                'thickness': 0.75,
                'value': 80
            }
        }
    ))
    fig_gauge.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=250,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

with col_summary:
    st.subheader("Match Summary Breakdown")
    
    total_skills = len(matching_skills) + len(missing_skills)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
            <div class="metric-card">
                <h3>Matched Skills</h3>
                <div class="metric-value" style="color: #4ADE80;">{len(matching_skills)}</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class="metric-card">
                <h3>Missing Skills</h3>
                <div class="metric-value" style="color: #FCA5A5;">{len(missing_skills)}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Plotly Skill Coverage Donut Chart
    if total_skills > 0:
        fig_donut = px.pie(
            names=["Matching Skills", "Missing Skills"],
            values=[len(matching_skills), len(missing_skills)],
            color_discrete_sequence=["#22C55E", "#EF4444"],
            hole=0.55
        )
        fig_donut.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=150,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False
        )
        st.plotly_chart(fig_donut, use_container_width=True)

st.divider()

# --- Section 2: Skill Badges & Gap Analysis ---
st.subheader("🎯 Skill Gap Breakdown")

col_match, col_miss = st.columns(2)

with col_match:
    st.markdown("### Matching Skills Found")
    if matching_skills:
        badges_match = " ".join([f'<span class="badge-match">✔ {s}</span>' for s in matching_skills])
        st.markdown(badges_match, unsafe_allow_html=True)
    else:
        st.info("No explicit technical skill matches detected.")

with col_miss:
    st.markdown("### Missing / Desirable Keywords")
    if missing_skills:
        badges_miss = " ".join([f'<span class="badge-missing">✖ {s}</span>' for s in missing_skills])
        st.markdown(badges_miss, unsafe_allow_html=True)
    else:
        st.success("Great job! All required skills from the job posting are present.")

st.divider()

# --- Section 3: Actionable AI Suggestions ---
st.subheader("💡 Actionable Recommendations")

if suggestions:
    for idx, sugg in enumerate(suggestions, 1):
        st.info(f"**Recommendation #{idx}:** {sugg}")
else:
    st.write("No additional suggestions provided.")

st.divider()

# --- Navigation Action to Improvement Phase ---
col_impr, _ = st.columns([1, 1])
with col_impr:
    if st.button("🚀 Proceed to Improve Resume (Phase 9)", type="primary", use_container_width=True):
        st.switch_page("pages/5_Improve_Resume.py")