import re
from typing import List, Dict

# Standard tech and domain skill keywords for pattern matching
COMMON_SKILLS_DB = [
    "Python", "Java", "C++", "JavaScript", "TypeScript", "React", "Node.js",
    "SQL", "PostgreSQL", "MySQL", "MongoDB", "SQLite", "Redis",
    "Docker", "Kubernetes", "AWS", "Azure", "GCP", "DevOps", "CI/CD",
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
    "PyTorch", "TensorFlow", "Scikit-Learn", "Pandas", "NumPy",
    "FastAPI", "Flask", "Django", "Streamlit", "REST API", "GraphQL",
    "Git", "GitHub", "Linux", "Agile", "Scrum", "BentoML", "Microservices"
]

def extract_keywords_from_jd(jd_text: str) -> Dict[str, List[str]]:
    """
    Extracts highlighted tech skills and responsibility bullet points from raw JD text.
    """
    if not jd_text:
        return {"found_skills": [], "key_requirements": []}

    # Extract matching skills (case-insensitive boundary check)
    found_skills = []
    for skill in COMMON_SKILLS_DB:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, jd_text, re.IGNORECASE):
            found_skills.append(skill)

    # Extract candidate responsibility/requirement sentences
    lines = [line.strip() for line in jd_text.split("\n") if line.strip()]
    key_requirements = []
    
    for line in lines:
        if line.startswith(("•", "-", "*", "1.", "2.", "3.", "4.", "5.")):
            cleaned = re.sub(r'^[•\-\*\d\.\s]+', '', line).strip()
            if len(cleaned) > 15:
                key_requirements.append(cleaned)

    # Fallback to standard sentences if no bullet points found
    if not key_requirements:
        sentences = re.split(r'(?<=[.!?]) +', jd_text)
        key_requirements = [s.strip() for s in sentences if len(s.strip()) > 20][:5]

    return {
        "found_skills": list(set(found_skills)),
        "key_requirements": key_requirements[:7]
    }