import streamlit as st
from models.schema import CandidateProfile, ExperienceSchema, ProjectSchema
from database.queries import save_candidate_profile, get_candidate_profile
from database.database import init_db

# Ensure DB tables exist
init_db()

st.title("👤 Candidate Profile")
st.caption("Manage your background, technical skills, experience, and projects.")

# Load existing profile from SQLite into session_state if available
existing_profile = get_candidate_profile()

if "profile_loaded" not in st.session_state:
    if existing_profile:
        st.session_state.name = existing_profile.name
        st.session_state.email = existing_profile.email
        st.session_state.phone = existing_profile.phone
        st.session_state.linkedin = existing_profile.linkedin
        st.session_state.github = existing_profile.github
        st.session_state.portfolio = existing_profile.portfolio
        st.session_state.summary = existing_profile.summary
        st.session_state.skills_str = ", ".join(existing_profile.skills)
        st.session_state.experiences = [
            {
                "company": e.company,
                "role": e.role,
                "duration": e.duration,
                "description": e.description,
            }
            for e in existing_profile.experiences
        ]
        st.session_state.projects = [
            {
                "title": p.title,
                "technologies": p.technologies,
                "description": p.description,
            }
            for p in existing_profile.projects
        ]
    else:
        # Default empty structures
        st.session_state.name = ""
        st.session_state.email = ""
        st.session_state.phone = ""
        st.session_state.linkedin = ""
        st.session_state.github = ""
        st.session_state.portfolio = ""
        st.session_state.summary = ""
        st.session_state.skills_str = ""
        st.session_state.experiences = [
            {"company": "", "role": "", "duration": "", "description": ""}
        ]
        st.session_state.projects = [
            {"title": "", "technologies": "", "description": ""}
        ]
    st.session_state.profile_loaded = True

# --- Form Section 1: Personal Details ---
st.subheader("1. Personal Details")
col1, col2 = st.columns(2)

with col1:
    name = st.text_input("Full Name", value=st.session_state.name)
    email = st.text_input("Email Address", value=st.session_state.email)
    phone = st.text_input("Phone Number", value=st.session_state.phone)

with col2:
    linkedin = st.text_input("LinkedIn Profile URL", value=st.session_state.linkedin)
    github = st.text_input("GitHub Profile URL", value=st.session_state.github)
    portfolio = st.text_input("Portfolio Website URL", value=st.session_state.portfolio)

st.divider()

# --- Form Section 2: Summary & Skills ---
st.subheader("2. Professional Summary & Core Skills")
summary = st.text_area(
    "Professional Summary",
    value=st.session_state.summary,
    height=120,
    placeholder="e.g., Software Engineer with 3+ years of experience building scalable Web APIs and ML applications...",
)

skills_str = st.text_input(
    "Technical Skills (comma-separated)",
    value=st.session_state.skills_str,
    placeholder="Python, Streamlit, SQL, Scikit-Learn, Docker, REST APIs, Git",
)

st.divider()

# --- Form Section 3: Work Experience (Dynamic) ---
st.subheader("3. Work Experience")

# Control buttons for Experience
exp_col1, exp_col2, _ = st.columns([1, 1, 4])
with exp_col1:
    if st.button("➕ Add Experience"):
        st.session_state.experiences.append(
            {"company": "", "role": "", "duration": "", "description": ""}
        )
        st.rerun()

with exp_col2:
    if st.button("➖ Remove Last") and len(st.session_state.experiences) > 1:
        st.session_state.experiences.pop()
        st.rerun()

# Dynamic Input Cards for Experience
updated_experiences = []
for idx, exp in enumerate(st.session_state.experiences):
    with st.expander(f"Experience #{idx + 1} — {exp.get('company') or 'New Role'}", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            comp = st.text_input(f"Company Name", value=exp["company"], key=f"exp_company_{idx}")
        with c2:
            role = st.text_input(f"Role / Title", value=exp["role"], key=f"exp_role_{idx}")
        with c3:
            dur = st.text_input(f"Duration", value=exp["duration"], key=f"exp_dur_{idx}", placeholder="e.g. June 2024 - Present")
        
        desc = st.text_area(
            f"Key Responsibilities & Achievements",
            value=exp["description"],
            key=f"exp_desc_{idx}",
            height=100,
            placeholder="• Engineered REST endpoints lowering latency by 20%...\n• Built ML pipelines using PyTorch...",
        )
        updated_experiences.append(
            {"company": comp, "role": role, "duration": dur, "description": desc}
        )

st.session_state.experiences = updated_experiences

st.divider()

# --- Form Section 4: Projects (Dynamic) ---
st.subheader("4. Projects")

proj_col1, proj_col2, _ = st.columns([1, 1, 4])
with proj_col1:
    if st.button("➕ Add Project"):
        st.session_state.projects.append(
            {"title": "", "technologies": "", "description": ""}
        )
        st.rerun()

with proj_col2:
    if st.button("➖ Remove Project") and len(st.session_state.projects) > 1:
        st.session_state.projects.pop()
        st.rerun()

updated_projects = []
for idx, proj in enumerate(st.session_state.projects):
    with st.expander(f"Project #{idx + 1} — {proj.get('title') or 'New Project'}", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            title = st.text_input(f"Project Title", value=proj["title"], key=f"proj_title_{idx}")
        with c2:
            techs = st.text_input(f"Technologies Used", value=proj["technologies"], key=f"proj_tech_{idx}", placeholder="Python, BentoML, Docker")
        
        desc = st.text_area(
            f"Description & Impact",
            value=proj["description"],
            key=f"proj_desc_{idx}",
            height=90,
            placeholder="Developed an automated containerized API for real-time model inference...",
        )
        updated_projects.append(
            {"title": title, "technologies": techs, "description": desc}
        )

st.session_state.projects = updated_projects

st.divider()

# --- Save Action ---
if st.button("💾 Save Full Profile to Database", type="primary", use_container_width=True):
    if not name or not email:
        st.error("Name and Email are required fields.")
    else:
        # Convert skills string to clean list
        parsed_skills = [s.strip() for s in skills_str.split(",") if s.strip()]

        # Convert state structures to Pydantic objects
        exp_models = [
            ExperienceSchema(
                company=e["company"],
                role=e["role"],
                duration=e["duration"],
                description=e["description"],
            )
            for e in st.session_state.experiences
            if e["company"].strip() or e["role"].strip()
        ]

        proj_models = [
            ProjectSchema(
                title=p["title"],
                technologies=p["technologies"],
                description=p["description"],
            )
            for p in st.session_state.projects
            if p["title"].strip()
        ]

        profile_payload = CandidateProfile(
            name=name,
            email=email,
            phone=phone,
            linkedin=linkedin,
            github=github,
            portfolio=portfolio,
            summary=summary,
            skills=parsed_skills,
            experiences=exp_models,
            projects=proj_models,
        )

        cand_id = save_candidate_profile(profile_payload)
        st.success(f"Candidate Profile successfully saved to database (Candidate ID: {cand_id})!")