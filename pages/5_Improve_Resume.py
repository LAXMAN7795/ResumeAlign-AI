import streamlit as st
from database.queries import get_latest_job_description, save_generated_resume
from database.database import init_db
from services.prompt_service import build_improver_prompt
from services.llm_service import generate_text
from services.export_pdf import markdown_to_pdf_bytes
from services.export_docx import markdown_to_docx_bytes

# Ensure database tables exist
init_db()

st.title("🚀 Improve Resume")
st.caption("Apply AI analysis recommendations to refine your resume bullet points and raise your ATS match score.")

# Retrieve current resume and analysis results from session state
current_resume = st.session_state.get("current_generated_resume")
analysis_results = st.session_state.get("analysis_results", {})
latest_jd = get_latest_job_description()

if not current_resume:
    st.warning("⚠️ No active generated resume found! Please generate a resume first.")
    if st.button("👉 Go to Resume Generator"):
        st.switch_page("pages/3_Generate_Resume.py")
    st.stop()

missing_skills = analysis_results.get("missing_skills", [])
suggestions = analysis_results.get("suggestions", [])
current_ats = analysis_results.get("ats_score", 0)

# --- Active Feedback Context Banner ---
col_score, col_feedback = st.columns([1, 2])

with col_score:
    st.markdown(f"""
        <div class="metric-card">
            <h3>Current ATS Score</h3>
            <div class="metric-value" style="color: #2563EB;">{current_ats}%</div>
        </div>
    """, unsafe_allow_html=True)

with col_feedback:
    st.subheader("Target Feedback to Integrate")
    if missing_skills:
        st.markdown("**Missing Keywords to Target:**")
        badges = " ".join([f'<span class="badge-missing">{s}</span>' for s in missing_skills])
        st.markdown(badges, unsafe_allow_html=True)
    
    if suggestions:
        st.markdown("**Key Actionable Recommendations:**")
        for s in suggestions[:3]:
            st.write(f"• {s}")

st.divider()

# --- Model Selector for Improvement Pipeline ---
with st.expander("⚙️ Improvement Engine & Model Selection", expanded=False):
    provider = st.radio("Select Provider", ["Google Gemini", "Groq"], horizontal=True, key="improver_provider")
    
    if provider == "Google Gemini":
        selected_model = st.selectbox(
            "Select Gemini Model",
            ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.5-pro"],
            index=0,
            key="improver_gemini_model",
            help="gemini-2.5-flash is ideal for fast, high-quality bullet refinement."
        )
    else:
        selected_model = st.selectbox(
            "Select Groq Model",
            ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"],
            index=0,
            key="improver_groq_model"
        )

# Action to trigger AI improvement
if st.button("✨ Refine Resume Content with AI", type="primary", use_container_width=True):
    with st.spinner("🤖 Applying ATS suggestions & quantifying bullet achievements..."):
        try:
            prompt = build_improver_prompt(current_resume, missing_skills, suggestions)
            improved_markdown = generate_text(prompt, model_name=selected_model)
            
            st.session_state["improved_resume_markdown"] = improved_markdown
            st.success("Resume improvements successfully generated!")
        except Exception as e:
            st.error(f"Improvement process failed: {str(e)}")

st.divider()

# --- Side-by-Side Comparison Workspace ---
active_display_content = st.session_state.get("improved_resume_markdown", current_resume)

if "improved_resume_markdown" in st.session_state:
    st.subheader("↔️ Side-by-Side Comparison & Workspace")
    
    col_orig, col_impr = st.columns(2)
    
    with col_orig:
        st.markdown("### Original Version")
        st.text_area(
            "Original Markdown Source",
            value=current_resume,
            height=420,
            disabled=True,
            key="orig_area"
        )

    with col_impr:
        st.markdown("### AI-Improved Version")
        edited_improved = st.text_area(
            "Improved Markdown Source (Editable)",
            value=st.session_state["improved_resume_markdown"],
            height=420,
            key="impr_area"
        )
        st.session_state["improved_resume_markdown"] = edited_improved
        active_display_content = edited_improved

    st.divider()

    col_apply, col_reanalyze = st.columns(2)

    with col_apply:
        if st.button("✅ Accept & Set as Active Resume", type="primary", use_container_width=True):
            st.session_state["current_generated_resume"] = st.session_state["improved_resume_markdown"]
            
            # Save updated draft to database if active candidate context exists
            if "active_candidate_id" in st.session_state and "active_jd_id" in st.session_state:
                from models.schema import ResumeRecord
                record = ResumeRecord(
                    candidate_id=st.session_state["active_candidate_id"],
                    jd_id=st.session_state["active_jd_id"],
                    generated_markdown=st.session_state["improved_resume_markdown"],
                    ats_score=current_ats
                )
                save_generated_resume(record)

            st.success("Active resume updated and saved! You can now re-run analysis or download.")

    with col_reanalyze:
        if st.button("📊 Re-Analyze Improved Resume", use_container_width=True):
            st.session_state["current_generated_resume"] = st.session_state["improved_resume_markdown"]
            st.switch_page("pages/4_Resume_Analysis.py")

st.divider()

# --- Phase 10: Multi-Format Export Section ---
st.subheader("📥 Export & Download Resume")
c_pdf, c_docx, c_md = st.columns(3)

with c_pdf:
    try:
        pdf_bytes = markdown_to_pdf_bytes(active_display_content)
        st.download_button(
            label="📄 Download PDF",
            data=pdf_bytes,
            file_name="Improved_ATS_Resume.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"PDF Export Error: {e}")

with c_docx:
    try:
        docx_bytes = markdown_to_docx_bytes(active_display_content)
        st.download_button(
            label="📝 Download DOCX",
            data=docx_bytes,
            file_name="Improved_ATS_Resume.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"DOCX Export Error: {e}")

with c_md:
    st.download_button(
        label="💻 Download Markdown",
        data=active_display_content.encode('utf-8'),
        file_name="Improved_ATS_Resume.md",
        mime="text/markdown",
        use_container_width=True
    )