import streamlit as st
from database.queries import get_full_resume_history, delete_resume_history_record
from database.database import init_db
from services.export_pdf import markdown_to_pdf_bytes
from services.export_docx import markdown_to_docx_bytes

# Ensure database tables exist
init_db()

st.title("📜 Resume Generation History")
st.caption("Review past optimization sessions, inspect saved Markdown source, and export previous versions.")

history_records = get_full_resume_history()

if not history_records:
    st.info("No saved resume generations found. Generate your first resume in the Resume Generator page!")
    if st.button("👉 Go to Resume Generator"):
        st.switch_page("pages/3_Generate_Resume.py")
    st.stop()

# --- Summary Metrics Bar ---
col_total, col_avg, col_latest = st.columns(3)

scores = [r["ats_score"] for r in history_records if r["ats_score"] > 0]
avg_score = round(sum(scores) / len(scores), 1) if scores else "N/A"

with col_total:
    st.markdown(f"""
        <div class="metric-card">
            <h3>Total Resumes Saved</h3>
            <div class="metric-value">{len(history_records)}</div>
        </div>
    """, unsafe_allow_html=True)

with col_avg:
    st.markdown(f"""
        <div class="metric-card">
            <h3>Average ATS Score</h3>
            <div class="metric-value" style="color: #4ADE80;">{avg_score}{'%' if avg_score != 'N/A' else ''}</div>
        </div>
    """, unsafe_allow_html=True)

with col_latest:
    st.markdown(f"""
        <div class="metric-card">
            <h3>Latest Target Position</h3>
            <div class="metric-value" style="font-size: 1.2rem; margin-top: 10px;">{history_records[0]['job_title']}</div>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# --- History Records Inspection Workspace ---
st.subheader("📌 Saved Resume Records")

for item in history_records:
    score_display = f"{item['ats_score']}%" if item['ats_score'] > 0 else "Unscored"
    card_title = f"📄 {item['job_title']} at {item['company']} — ATS Score: {score_display} ({item['created_at']})"
    
    with st.expander(card_title, expanded=False):
        c_meta, c_actions = st.columns([2, 1])
        
        with c_meta:
            st.write(f"**Record ID:** #{item['id']}")
            st.write(f"**Candidate:** {item['candidate_name']}")
            st.write(f"**Target Position:** {item['job_title']} ({item['company']})")
            st.write(f"**Created At:** {item['created_at']}")

        with c_actions:
            if st.button(f"🔄 Reload into Active Session", key=f"reload_{item['id']}", use_container_width=True):
                st.session_state["current_generated_resume"] = item["generated_markdown"]
                st.session_state["active_candidate_id"] = item["candidate_id"]
                st.session_state["active_jd_id"] = item["jd_id"]
                st.success(f"Resume #{item['id']} loaded as active session!")
                st.switch_page("pages/3_Generate_Resume.py")

            if st.button(f"🗑️ Delete Record", key=f"del_{item['id']}", use_container_width=True):
                delete_resume_history_record(item["id"])
                st.success(f"Record #{item['id']} deleted.")
                st.rerun()

        st.divider()
        
        # Markdown & Render Preview Tabs
        tab_md, tab_preview, tab_download = st.tabs(["💻 Raw Markdown", "👁️ Live Render", "📥 Quick Export"])

        with tab_md:
            st.code(item["generated_markdown"], language="markdown")

        with tab_preview:
            st.markdown(item["generated_markdown"])

        with tab_download:
            c_pdf, c_docx, c_raw_md = st.columns(3)
            
            with c_pdf:
                try:
                    pdf_bytes = markdown_to_pdf_bytes(item["generated_markdown"])
                    st.download_button(
                        label="📄 Download PDF",
                        data=pdf_bytes,
                        file_name=f"Resume_Record_{item['id']}.pdf",
                        mime="application/pdf",
                        key=f"dl_pdf_{item['id']}",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"PDF Error: {e}")

            with c_docx:
                try:
                    docx_bytes = markdown_to_docx_bytes(item["generated_markdown"])
                    st.download_button(
                        label="📝 Download DOCX",
                        data=docx_bytes,
                        file_name=f"Resume_Record_{item['id']}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key=f"dl_docx_{item['id']}",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"DOCX Error: {e}")

            with c_raw_md:
                st.download_button(
                    label="💻 Download Markdown",
                    data=item["generated_markdown"].encode('utf-8'),
                    file_name=f"Resume_Record_{item['id']}.md",
                    mime="text/markdown",
                    key=f"dl_md_{item['id']}",
                    use_container_width=True
                )