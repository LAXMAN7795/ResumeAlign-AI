from database.database import get_connection
from models.schema import CandidateProfile, ExperienceSchema, ProjectSchema, JobDescription, ResumeRecord
from typing import Optional, List, Dict, Any

# ==========================================
# CANDIDATE PROFILE CRUD OPERATIONS
# ==========================================

def save_candidate_profile(profile: CandidateProfile) -> int:
    """
    Insert or update candidate profile along with relational skills, 
    experiences, and projects in SQLite.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Check if a candidate profile already exists (Single User SaaS model)
    cursor.execute("SELECT id FROM candidate LIMIT 1")
    row = cursor.fetchone()

    if row:
        candidate_id = row["id"]
        cursor.execute("""
            UPDATE candidate
            SET name = ?, email = ?, phone = ?, linkedin = ?, github = ?, portfolio = ?, summary = ?
            WHERE id = ?
        """, (
            profile.name, 
            profile.email, 
            profile.phone, 
            profile.linkedin, 
            profile.github, 
            profile.portfolio, 
            profile.summary, 
            candidate_id
        ))
        
        # Clear existing relational records for clean update
        cursor.execute("DELETE FROM skills WHERE candidate_id = ?", (candidate_id,))
        cursor.execute("DELETE FROM experience WHERE candidate_id = ?", (candidate_id,))
        cursor.execute("DELETE FROM projects WHERE candidate_id = ?", (candidate_id,))
    else:
        cursor.execute("""
            INSERT INTO candidate (name, email, phone, linkedin, github, portfolio, summary)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            profile.name, 
            profile.email, 
            profile.phone, 
            profile.linkedin, 
            profile.github, 
            profile.portfolio, 
            profile.summary
        ))
        candidate_id = cursor.lastrowid

    # Insert Skills
    for skill in profile.skills:
        if skill.strip():
            cursor.execute("INSERT INTO skills (candidate_id, skill_name) VALUES (?, ?)", (candidate_id, skill.strip()))

    # Insert Work Experiences
    for exp in profile.experiences:
        cursor.execute("""
            INSERT INTO experience (candidate_id, company, role, duration, description)
            VALUES (?, ?, ?, ?, ?)
        """, (candidate_id, exp.company, exp.role, exp.duration, exp.description))

    # Insert Projects
    for proj in profile.projects:
        cursor.execute("""
            INSERT INTO projects (candidate_id, title, description, technologies)
            VALUES (?, ?, ?, ?)
        """, (candidate_id, proj.title, proj.description, proj.technologies))

    conn.commit()
    conn.close()
    return candidate_id


def get_candidate_profile() -> Optional[CandidateProfile]:
    """Retrieve the active candidate profile with all relational skills, experience, and projects."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM candidate LIMIT 1")
    cand_row = cursor.fetchone()
    if not cand_row:
        conn.close()
        return None

    candidate_id = cand_row["id"]

    # Fetch skills
    cursor.execute("SELECT skill_name FROM skills WHERE candidate_id = ?", (candidate_id,))
    skills = [r["skill_name"] for r in cursor.fetchall()]

    # Fetch experiences
    cursor.execute("SELECT * FROM experience WHERE candidate_id = ?", (candidate_id,))
    experiences = [
        ExperienceSchema(
            company=r["company"],
            role=r["role"],
            duration=r["duration"],
            description=r["description"]
        ) for r in cursor.fetchall()
    ]

    # Fetch projects
    cursor.execute("SELECT * FROM projects WHERE candidate_id = ?", (candidate_id,))
    projects = [
        ProjectSchema(
            title=r["title"],
            description=r["description"],
            technologies=r["technologies"]
        ) for r in cursor.fetchall()
    ]

    conn.close()

    return CandidateProfile(
        id=candidate_id,
        name=cand_row["name"],
        email=cand_row["email"],
        phone=cand_row["phone"] or "",
        linkedin=cand_row["linkedin"] or "",
        github=cand_row["github"] or "",
        portfolio=cand_row["portfolio"] or "",
        summary=cand_row["summary"] or "",
        skills=skills,
        experiences=experiences,
        projects=projects
    )

# ==========================================
# JOB DESCRIPTION CRUD OPERATIONS
# ==========================================

def save_job_description(jd: JobDescription) -> int:
    """Save a target job description posting into SQLite."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO job_descriptions (title, company, raw_text)
        VALUES (?, ?, ?)
    """, (jd.title, jd.company, jd.raw_text))
    jd_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return jd_id


def get_latest_job_description() -> Optional[JobDescription]:
    """Retrieve the most recently saved job description target."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM job_descriptions ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    if row:
        return JobDescription(
            id=row["id"],
            title=row["title"],
            company=row["company"],
            raw_text=row["raw_text"],
            created_at=row["created_at"]
        )
    return None

# ==========================================
# RESUME HISTORY & GENERATION OPERATIONS
# ==========================================

def save_generated_resume(resume: ResumeRecord) -> int:
    """Save or insert a generated resume record into history."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO resumes (candidate_id, jd_id, generated_markdown, ats_score)
        VALUES (?, ?, ?, ?)
    """, (resume.candidate_id, resume.jd_id, resume.generated_markdown, resume.ats_score))
    res_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return res_id


def get_full_resume_history() -> List[Dict[str, Any]]:
    """Fetch all saved resume generations joined with target job details."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            r.id, 
            r.candidate_id, 
            r.jd_id, 
            r.generated_markdown, 
            r.ats_score, 
            r.created_at,
            jd.title AS job_title, 
            jd.company,
            c.name AS candidate_name
        FROM resumes r
        JOIN job_descriptions jd ON r.jd_id = jd.id
        JOIN candidate c ON r.candidate_id = c.id
        ORDER BY r.id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_resume_history_record(resume_id: int) -> bool:
    """Delete a specific resume record from SQLite history by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM resumes WHERE id = ?", (resume_id,))
    conn.commit()
    conn.close()
    return True