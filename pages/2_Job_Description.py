import streamlit as st
from models.schema import JobDescription
from database.queries import save_job_description, get_latest_job_description
from database.database import get_connection, init_db
from services.parser import extract_keywords_from_jd

# Ensure DB tables exist
init_db()

st.title("📄 Job Description Management")
st.caption("Paste job postings, extract key skills automatically, and save targets for resume optimization.")

# Fetch history of saved job descriptions
def get_all_job_descriptions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, company, created_at, raw_text FROM job_descriptions ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

saved_jds = get_all_job_descriptions()

# --- Tab Layout ---
tab1, tab2 = st.tabs(["➕ Add New Target JD", "📜 Saved Target Positions"])

with tab1:
    st.subheader("Target Position Information")
    
    col1, col2 = st.columns(2)
    with col1:
        job_title = st.text_input("Target Job Title", placeholder="e.g. Senior Machine Learning Engineer")
    with col2:
        company = st.text_input("Company Name", placeholder="e.g. Google / Acme Corp")

    raw_jd = st.text_area(
        "Raw Job Description / Requirements",
        height=220,
        placeholder="Paste full job duties, qualifications, and required skills here..."
    )

    # Real-time keyword extraction preview
    if raw_jd.strip():
        parsed_data = extract_keywords_from_jd(raw_jd)
        
        st.markdown("### 🔍 Real-time Extracted Skill Keywords")
        if parsed_data["found_skills"]:
            badges_html = " ".join([f'<span class="badge-match">{s}</span>' for s in parsed_data["found_skills"]])
            st.markdown(badges_html, unsafe_allow_html=True)
        else:
            st.info("No common tech keywords auto-detected yet. You can still save this description.")

        if parsed_data["key_requirements"]:
            with st.expander("Key Detected Responsibilities / Requirements"):
                for req in parsed_data["key_requirements"]:
                    st.write(f"• {req}")

    st.divider()

    if st.button("💾 Save Target Job Description", type="primary", use_container_width=True):
        if not job_title or not raw_jd:
            st.error("Please provide both a Job Title and the raw Job Description.")
        else:
            jd_payload = JobDescription(
                title=job_title,
                company=company or "N/A",
                raw_text=raw_jd
            )
            jd_id = save_job_description(jd_payload)
            st.success(f"Job Description saved successfully (ID: {jd_id})!")
            st.rerun()

with tab2:
    st.subheader("Saved Target Positions")
    if not saved_jds:
        st.info("No job descriptions saved yet. Add one in the first tab.")
    else:
        for item in saved_jds:
            with st.expander(f"📌 {item['title']} at {item['company']} (Saved: {item['created_at']})"):
                st.markdown("**Raw Job Description:**")
                st.text(item['raw_text'][:400] + ("..." if len(item['raw_text']) > 400 else ""))
                
                parsed = extract_keywords_from_jd(item['raw_text'])
                if parsed["found_skills"]:
                    st.markdown("**Detected Key Skills:**")
                    badges = " ".join([f'<span class="badge-match">{s}</span>' for s in parsed["found_skills"]])
                    st.markdown(badges, unsafe_allow_html=True)