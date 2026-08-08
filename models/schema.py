from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

# --- Candidate Profile Models ---

class SkillSchema(BaseModel):
    name: str

class ProjectSchema(BaseModel):
    title: str
    description: str
    technologies: str  # Comma-separated list of tech used

class ExperienceSchema(BaseModel):
    company: str
    role: str
    duration: str
    description: str

class CandidateProfile(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    phone: str
    linkedin: Optional[str] = ""
    github: Optional[str] = ""
    portfolio: Optional[str] = ""
    summary: str
    skills: List[str] = []
    experiences: List[ExperienceSchema] = []
    projects: List[ProjectSchema] = []

# --- Job Description Model ---

class JobDescription(BaseModel):
    id: Optional[int] = None
    title: str
    company: str
    raw_text: str
    created_at: Optional[str] = None

# --- Resume Model ---

class ResumeRecord(BaseModel):
    id: Optional[int] = None
    candidate_id: int
    jd_id: int
    generated_markdown: str
    ats_score: int
    created_at: Optional[str] = None