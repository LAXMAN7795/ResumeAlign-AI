import streamlit as st
from database.queries import get_candidate_profile, get_latest_job_description, save_generated_resume
from database.database import init_db
from services.prompt_service import build_generator_prompt
from services.llm_service import generate_text
from services.export_pdf import markdown_to_pdf_bytes
from services.export_docx import markdown_to_docx_bytes

# Ensure database tables exist
init_db()

st.title("✨ Resume Generator")
st.caption("Synthesize your saved Candidate Profile and Target Job Description into an ATS-aligned Markdown resume.")

# Retrieve Candidate Profile and Job Description from SQLite
profile = get_candidate_profile()
latest_jd = get_latest_job_description()

# Guardrails to ensure prerequisite data is present
if not profile:
    st.warning("⚠️ No Candidate Profile found! Please complete your profile first.")
    if st.button("👉 Go to Candidate Profile"):
        st.switch_page("pages/1_Profile.py")
    st.stop()

if not latest_jd:
    st.warning("⚠️ No Target Job Description found! Please save a job target first.")
    if st.button("👉 Go to Job Description"):
        st.switch_page("pages/2_Job_Description.py")
    st.stop()

# --- Summary Cards of Active Context ---
col1, col2 = st.columns(2)

with col1:
    with st.expander("👤 Active Candidate Profile", expanded=False):
        st.write(f"**Name:** {profile.name}")
        st.write(f"**Email:** {profile.email}")
        st.write(f"**Skills:** {', '.join(profile.skills)}")
        st.write(f"**Experiences:** {len(profile.experiences)} entry/entries")
        st.write(f"**Projects:** {len(profile.projects)} entry/entries")

with col2:
    with st.expander("📄 Target Job Description", expanded=False):
        st.write(f"**Title:** {latest_jd.title}")
        st.write(f"**Company:** {latest_jd.company}")
        st.text_area("JD Preview", value=latest_jd.raw_text[:300] + "...", height=100, disabled=True)

st.divider()

# --- LLM Provider & Model Selection ---
with st.expander("⚙️ LLM Provider & Model Selection", expanded=False):
    provider = st.radio("Select Provider", ["Google Gemini", "Groq"], horizontal=True, key="gen_provider")
    
    if provider == "Google Gemini":
        selected_model = st.selectbox(
            "Select Gemini Model",
            ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.5-pro"],
            index=0,
            key="gen_gemini_model",
            help="gemini-2.5-flash is recommended for fast, high-quality resume generation."
        )
    else:
        selected_model = st.selectbox(
            "Select Groq Model",
            ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"],
            index=0,
            key="gen_groq_model"
        )

# Main Generation Action
if st.button("⚡ Generate Tailored ATS Resume", type="primary", use_container_width=True):
    with st.spinner("🤖 Synthesizing profile & analyzing JD keywords via LLM..."):
        try:
            # Build structured prompt strictly anchored to candidate facts
            prompt = build_generator_prompt(profile, latest_jd)
            
            # Call LLM
            generated_markdown = generate_text(prompt, model_name=selected_model)
            
            # Store result in session state
            st.session_state["current_generated_resume"] = generated_markdown
            st.session_state["active_jd_id"] = latest_jd.id
            st.session_state["active_candidate_id"] = profile.id
            
            # Save draft to history database
            from models.schema import ResumeRecord
            record = ResumeRecord(
                candidate_id=profile.id,
                jd_id=latest_jd.id,
                generated_markdown=generated_markdown,
                ats_score=0
            )
            save_generated_resume(record)

            st.success("✨ Resume tailored and generated successfully!")
        except Exception as e:
            st.error(f"Generation failed: {str(e)}")

# Display Generated Output, Workspace & Export Options
if "current_generated_resume" in st.session_state:
    st.divider()
    st.subheader("📄 Generated Resume Workspace")
    
    tab_edit, tab_preview = st.tabs(["✏️ Edit Markdown Source", "👁️ Live Rendered Preview"])
    
    with tab_edit:
        edited_markdown = st.text_area(
            "Markdown Source Code",
            value=st.session_state["current_generated_resume"],
            height=450,
            key="markdown_editor"
        )
        st.session_state["current_generated_resume"] = edited_markdown

    with tab_preview:
        st.markdown(st.session_state["current_generated_resume"])

    st.divider()

    # --- Phase 10: Multi-Format Export Buttons ---
    st.subheader("📥 Export & Download Resume")
    c_pdf, c_docx, c_md = st.columns(3)

    with c_pdf:
        try:
            pdf_data = markdown_to_pdf_bytes(st.session_state["current_generated_resume"])
            st.download_button(
                label="📄 Download PDF",
                data=pdf_data,
                file_name=f"{profile.name.replace(' ', '_')}_Resume_ATS.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"PDF Export Error: {e}")

    with c_docx:
        try:
            docx_data = markdown_to_docx_bytes(st.session_state["current_generated_resume"])
            st.download_button(
                label="📝 Download DOCX",
                data=docx_data,
                file_name=f"{profile.name.replace(' ', '_')}_Resume_ATS.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"DOCX Export Error: {e}")

    with c_md:
        st.download_button(
            label="💻 Download Markdown",
            data=st.session_state["current_generated_resume"].encode('utf-8'),
            file_name=f"{profile.name.replace(' ', '_')}_Resume_ATS.md",
            mime="text/markdown",
            use_container_width=True
        )

    st.divider()

    col_save, col_analyze = st.columns(2)
    with col_save:
        if st.button("💾 Update History Record", use_container_width=True):
            from models.schema import ResumeRecord
            record = ResumeRecord(
                candidate_id=st.session_state["active_candidate_id"],
                jd_id=st.session_state["active_jd_id"],
                generated_markdown=st.session_state["current_generated_resume"],
                ats_score=0
            )
            res_id = save_generated_resume(record)
            st.success(f"Resume updated in history (Record ID: {res_id})!")

    with col_analyze:
        if st.button("📊 Run ATS Analysis on this Resume", type="primary", use_container_width=True):
            st.switch_page("pages/4_Resume_Analysis.py")