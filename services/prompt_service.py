import json
from models.schema import CandidateProfile, JobDescription

def build_generator_prompt(profile: CandidateProfile, jd: JobDescription) -> str:
    """Build prompt for ATS resume generation strictly anchored to true candidate experience."""
    skills_formatted = ", ".join(profile.skills)
    
    exp_formatted = ""
    for idx, e in enumerate(profile.experiences, 1):
        exp_formatted += f"\nExperience #{idx}:\nCompany: {e.company}\nRole: {e.role}\nDuration: {e.duration}\nDetails: {e.description}\n"

    proj_formatted = ""
    for idx, p in enumerate(profile.projects, 1):
        proj_formatted += f"\nProject #{idx}:\nTitle: {p.title}\nTech: {p.technologies}\nDetails: {p.description}\n"

    return f"""You are an expert Executive Resume Writer and ATS Optimization Specialist.

TARGET JOB DESCRIPTION:
Title: {jd.title}
Company: {jd.company}
Requirements & Duties:
{jd.raw_text}

CANDIDATE TRUTH DATA:
Name: {profile.name}
Email: {profile.email} | Phone: {profile.phone}
LinkedIn: {profile.linkedin} | GitHub: {profile.github} | Portfolio: {profile.portfolio}
Summary: {profile.summary}
Skills: {skills_formatted}

Work Experience:
{exp_formatted}

Projects:
{proj_formatted}

INSTRUCTIONS & STRICT RULES:
1. Create a modern, high-impact Markdown resume tailored specifically to the target job description.
2. ANTI-HALLUCINATION GUARDRAIL: Do NOT invent skills, certifications, degrees, or job titles not provided in the Candidate Truth Data.
3. Optimize bullet points using active action verbs and result-driven phrases matching keywords from the Job Description where applicable.
4. Format cleanly using standard Markdown headings (e.g., # Name, ## Professional Summary, ## Technical Skills, ## Professional Experience, ## Projects).

Output ONLY the formatted Markdown resume."""


def build_analyzer_prompt(resume_markdown: str, jd_text: str) -> str:
    """Build prompt for ATS score and gap analysis with strict JSON schema response."""
    return f"""You are an advanced ATS (Applicant Tracking System) Evaluation Engine.

TARGET JOB DESCRIPTION:
{jd_text}

RESUME TO EVALUATE:
{resume_markdown}

INSTRUCTIONS:
Analyze the candidate's resume against the Job Description and return a JSON object with:
1. "ats_score": An integer from 0 to 100 representing job alignment.
2. "matching_skills": List of relevant skills/keywords found in BOTH the resume and JD.
3. "missing_skills": List of important skills/keywords requested in the JD but MISSING or weak in the resume.
4. "suggestions": List of 3 to 5 actionable, specific recommendations to improve the resume match.

STRICT JSON OUTPUT REQUIREMENT:
Return ONLY valid raw JSON with NO markdown code block wrappers (no ```json).

JSON format:
{{
  "ats_score": 85,
  "matching_skills": ["Python", "SQL"],
  "missing_skills": ["Docker", "Redis"],
  "suggestions": ["Include REST API achievements in project section"]
}}"""


def build_improver_prompt(resume_markdown: str, missing_skills: list, suggestions: list) -> str:
    """Build prompt to polish resume content based on analysis feedback."""
    missing_str = ", ".join(missing_skills) if missing_skills else "None"
    sugg_str = "\n".join([f"- {s}" for s in suggestions]) if suggestions else "Optimize bullet impact."

    return f"""You are an elite Resume Editor specializing in quantitative achievement framing.

CURRENT RESUME MARKDOWN:
{resume_markdown}

IDENTIFIED MISSING SKILLS/KEYWORDS:
{missing_str}

ACTIONABLE SUGGESTIONS:
{sugg_str}

INSTRUCTIONS:
1. Revise the Markdown resume to naturally address the suggestions and highlight relevant skills if supported by candidate background.
2. Quantify achievements where appropriate without fabricating false facts.
3. Maintain clear Markdown formatting.

Output ONLY the improved Markdown resume."""