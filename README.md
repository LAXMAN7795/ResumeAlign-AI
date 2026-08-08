# ResumeAlign AI — ATS Resume Optimization Platform

> **Live Application:** [resumealign-ai-laxman-sannu-gouda.streamlit.app](https://resumealign-ai-laxman-sannu-gouda.streamlit.app/)

**ResumeAlign AI** is an end-to-end, AI-powered Applicant Tracking System (ATS) resume optimization platform built with Python, Streamlit, and modern Large Language Models (Google Gemini 2.5 Flash & Groq Llama 3.3).

It bridges the gap between candidate qualifications and target job postings by extracting core skills, generating ATS-compliant tailored resumes, analyzing keyword gaps, providing actionable metric-driven feedback, and exporting formatted resumes to **PDF**, **DOCX**, and **Markdown**.

The core principle of the system is:

> **Optimize the candidate's resume for the target Job Description without inventing candidate information.**

---

## 📄 Executive Summary & Core Value Proposition

When applying for modern tech roles, candidate resumes are routinely filtered by Automated Tracking Systems (ATS) before reaching human recruiters. ResumeAlign AI solves this problem by ensuring:

1. **Fact-Anchored Generation:** Strictly enforces Candidate Truth Data to prevent AI hallucinations or fabricated experience.
2. **Contextual Skill Alignment:** Automatically parses target Job Descriptions (JDs) to identify high-value missing keywords and domain competencies.
3. **Iterative Refinement:** Provides real-time ATS match scoring (0-100%), Plotly gap visualization, side-by-side editing, and multi-format exports.

---

## 🛠️ Architecture & System Design

```
+-----------------------------------------------------------------------------------+
|                                 USER INTERFACE                                    |
|                      Streamlit Multi-Page SaaS Application                       |
|  [Dashboard]  [Profile]  [Job Desc]  [Generator]  [Analysis]  [Improver]  [History] |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                              BUSINESS & PARSER LAYER                              |
|   • Parser Service (Heuristic Tech Keyword Extraction)                            |
|   • Prompt Engineering Service (Fact-Anchored Context Builders & JSON Schemas)    |
|   • Export Engine (ReportLab PDF & python-docx Word Builder)                      |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------+     +-----------------------------------------+
|        LLM ENGINE ROUTER          |     |            DATA PERSISTENCE             |
|   • Google GenAI SDK (Gemini)     | <-> |  SQLite Database (resumealign.db)       |
|     - gemini-2.5-flash            |     |   • candidate (Profiles)                |
|     - gemini-2.5-flash-lite       |     |   • skills / experience / projects      |
|     - gemini-2.5-pro              |     |   • job_descriptions (Target JDs)       |
|   • Groq API Engine               |     |   • resumes (Markdown & ATS History)    |
|     - llama-3.3-70b-versatile     |     +-----------------------------------------+
|     - mixtral-8x7b-32768          |
+-----------------------------------+


```

## ✨ Features & Multi-Page SaaS Layout

The platform is designed as an enterprise-grade multi-page Streamlit application:

- **🏠 Executive Dashboard (****`app.py`****):** Overview metrics detailing candidate status, saved target JDs, average ATS match scores, and recommended optimization workflows.
- **👤 Candidate Profile (****`pages/1_Profile.py`****):** Dynamic multi-entry input forms for personal details, professional summary, technical skills, work experience, and projects mapped directly to SQLite.
- **📄 Job Description Management (****`pages/2_Job_Description.py`****):** Heuristic key-skill extractor parsing raw JD text for required technical skills and responsibilities in real time.
- **✨ Resume Generator (****`pages/3_Generate_Resume.py`****):** Multi-model LLM workspace synthesizing candidate facts and target JDs into structured, bullet-optimized Markdown resumes.
- **📊 ATS Analysis & Visual Dashboard (****`pages/4_Resume_Analysis.py`****):** Interactive Plotly gauge charts, skill coverage donut breakdown, matched vs. missing skill badges, and quantitative AI recommendations.
- **🚀 Resume Improver (****`pages/5_Improve_Resume.py`****):** Side-by-side comparison workspace allowing candidates to review AI-suggested bullet revisions, accept improvements, or re-analyze updated drafts.
- **📜 Resume History (****`pages/6_History.py`****):** Persistent record tracker to review past optimization sessions, inspect raw Markdown, reload previous drafts into active session memory, or download files.
- **⚙️ Settings (****`pages/7_Settings.py`****):** Session API key configuration management for Gemini and Groq model keys.

## 💻 Tech Stack & Dependencies

| **ComponentTechnology / LibraryDescription** |                                                  |                                                    |
| -------------------------------------------- | ------------------------------------------------ | -------------------------------------------------- |
| **Frontend Framework**                       | Streamlit (`>=1.31.0`)                           | Interactive multi-page Python web application      |
| **Core Language**                            | Python 3.10+                                     | Backend logic and orchestration                    |
| **LLM SDKs**                                 | `google-genai` (`>=0.1.0`), `groq` (`>=0.4.0`)   | Primary AI generation and fast inference engines   |
| **Database**                                 | SQLite3 + Pydantic (`>=2.6.0`)                   | Relational database storage with schema validation |
| **Data Visualizations**                      | Plotly (`>=5.18.0`)                              | Custom ATS gauges, donut charts, and skill metrics |
| **Document Exports**                         | ReportLab (`>=4.0.9`), `python-docx` (`>=1.1.0`) | Dynamic PDF & DOCX file conversion                 |
| **Environment Mgmt**                         | `python-dotenv` (`>=1.0.1`)                      | Local environment configuration                    |
| **Deployment**                               | Streamlit Cloud + GitHub                         | Continuous cloud hosting & secrets management      |

## 🗄️ Database Schema Design

The application uses an SQLite database (`database/resumealign.db`) enforcing strict foreign key constraints:

- **`candidate`**: Stores core personal info (Name, Email, Phone, LinkedIn, GitHub, Portfolio, Summary).
- **`skills`**: Relational candidate technical skills (`candidate_id`, `skill_name`).
- **`experience`**: Relational candidate employment history (`candidate_id`, `company`, `role`, `duration`, `description`).
- **`projects`**: Relational candidate project portfolio (`candidate_id`, `title`, `description`, `technologies`).
- **`job_descriptions`**: Target position repository (`id`, `title`, `company`, `raw_text`, `created_at`).
- **`resumes`**: Tailored generation history (`id`, `candidate_id`, `jd_id`, `generated_markdown`, `ats_score`, `created_at`).

## 🧠 LLM Architecture & Anti-Hallucination Guardrails

The application uses three structured prompt modules located in `services/prompt_service.py`:

1. **Resume Generator Prompt:** Combines candidate truth data with JD requirements. Features strict guardrails prohibiting the invention of unlisted degrees, skills, or job roles.
2. **Resume Analyzer Prompt:** Evaluates candidate-job fit and enforces strict JSON output containing:
   - `ats_score`: Integer (0-100)
   - `matching_skills`: Array of found keywords
   - `missing_skills`: Array of missing domain competencies
   - `suggestions`: Array of actionable improvement recommendations
3. **Resume Improver Prompt:** Refines bullet points by quantifying achievements and naturally integrating target keywords without fabricating facts.

## 📂 Actual Directory Structure

Plaintext

```
ResumeAlign-AI/
│
├── .streamlit/
│   └── config.toml            # Custom Slate/Blue SaaS theme configuration
│
├── assets/
│   └── css/
│        └── style.css          # Metric cards, custom badges & UI styling
│
├── database/
│   ├── database.py            # SQLite initialization & connection manager
│   ├── queries.py             # Centralized CRUD query functions
│   └── resumealign.db         # Local SQLite DB instance (Git ignored)
│
├── models/
│   └── schema.py              # Pydantic data schemas
│
├── pages/
│   ├── 1_Profile.py           # Candidate profile form module
│   ├── 2_Job_Description.py   # Target JD manager & skill parser
│   ├── 3_Generate_Resume.py   # AI Resume generator workspace
│   ├── 4_Resume_Analysis.py  # ATS match score & Plotly dashboard
│   ├── 5_Improve_Resume.py   # Side-by-side AI revision workspace
│   ├── 6_History.py           # Generation history & reloader
│   └── 7_Settings.py          # API key manager & cloud template
│
├── services/
│   ├── llm_service.py         # Unified Gemini & Groq LLM client engine
│   ├── prompt_service.py      # Fact-anchored prompts & JSON schemas
│   ├── parser.py              # Heuristic job description keyword parser
│   ├── export_pdf.py          # ReportLab PDF generator service
│   └── export_docx.py         # Python-docx Word generator service
│
├── utils/
│   └── constants.py           # App constants & metadata
│
├── app.py                     # Main application entrypoint & dashboard
├── requirements.txt           # Project dependencies
├── README.md                  # Project documentation
├── .env                       # Local environment file (Git ignored)
└── .gitignore                 # Version control exclusion rules


```

## 🚀 Local Installation & Setup

Follow these steps to run the application locally:

### 1. Clone the Repository

Bash

```
git clone [https://github.com/LAXMAN7795/ResumeAlign-AI.git](https://github.com/LAXMAN7795/ResumeAlign-AI.git)
cd ResumeAlign-AI


```

### 2. Create and Activate Virtual Environment

Bash

```
# Windows
python -m venv resume_venv
resume_venv\Scripts\activate

# macOS / Linux
python3 -m venv resume_venv
source resume_venv/bin/activate


```

### 3. Install Dependencies

Bash

```
pip install -r requirements.txt


```

### 4. Set Environment Variables

Create a `.env` file in the root directory:

Code snippet

```
GEMINI_API_KEY=your_google_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here


```

### 5. Launch Application

Bash

```
streamlit run app.py


```

Open your browser at `http://localhost:8501`.

## ☁️ Deployment on Streamlit Cloud

### 1. Push Your Project to GitHub

Ensure `.env` and `database/resumealign.db` are listed in `.gitignore`, then push your project:

Bash

```
git init
git add .
git commit -m "Deploying ResumeAlign AI SaaS application"
git branch -M main
git remote add origin [https://github.com/LAXMAN7795/ResumeAlign-AI.git](https://github.com/LAXMAN7795/ResumeAlign-AI.git)
git push -u origin main


```

### 2. Configure Streamlit Cloud

1. Log into [Streamlit Cloud](https://share.streamlit.io/) and click **New App**.
2. Select your repository `ResumeAlign-AI`, branch `main`, and set `app.py` as the entry point.
3. Open **Advanced Settings -> Secrets** and paste your API keys:

   Ini, TOML
   ```
   GEMINI_API_KEY = "your_actual_gemini_api_key"
   GROQ_API_KEY = "your_actual_groq_api_key"


   ```
4. Click **Deploy**.

👤 Author

Laxman Sannu Gouda

Generative AI Engineer | LLM Engineer | Agentic AI

Karnataka, India

LinkedIn: [https://www.linkedin.com/in/laxman-gouda](https://www.linkedin.com/in/laxman-gouda) GitHub: [https://github.com/LAXMAN7795](https://github.com/LAXMAN7795) Portfolio: [https://laxman7795.github.io/Portfolio-Laxman-Sannu-Gouda/](https://laxman7795.github.io/Portfolio-Laxman-Sannu-Gouda/) 📜 License

This project is developed as an AI engineering project and technical assignment.

License information can be added when the project is prepared for public distribution.