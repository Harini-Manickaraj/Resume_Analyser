"""
Resume Analyzer
AI Based Resume Intelligence and Job Recommendation System

Accepts a pre-parsed resume dictionary from parse_resume()
and produces a fully formatted response ready for the frontend.

Key fixes applied:
- dict input branch no longer discards the parsed profile by
  re-calling create_resume_profile(raw_text); it uses the dict
  directly.
- Sentence Transformer model is loaded ONCE per analyze_resume()
  call, not once per job.
- load_skill_dictionary() is called with the explicit file path
  so it matches the updated function signature.
- missing_skills stored as lists (not comma-joined strings)
  throughout so the skill-gap aggregation loop works correctly.
- Learning recommendations derived from skill-gap data.
- build_clean_response() is called before returning so the
  frontend receives a contract-stable flat object.
- experience_years pulled from profile correctly.
- One bad job record no longer crashes the whole pipeline.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

from backend.parsers.resume_parser import create_resume_profile
from backend.nlp.skill_extraction import (
    load_skill_dictionary,
    prepare_skill_dictionary,
    extract_skills,
    extract_skills_from_list,
)
from backend.analysis.response_formatter import build_clean_response


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "datasets"
SKILL_DICTIONARY_PATH = DATA_DIR / "skill_dictionary.csv"
JOB_DATASET_PATH = DATA_DIR / "job_descriptions.csv"


# =========================================================
# LOAD JOB DATASET
# =========================================================

def load_jobs() -> pd.DataFrame:
    if not JOB_DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Job description dataset not found: {JOB_DATASET_PATH}"
        )
    return pd.read_csv(JOB_DATASET_PATH).fillna("")


# =========================================================
# LOAD SKILL MAPPING
# =========================================================

def load_skills() -> Dict[str, str]:
    """
    Returns a flat alias→canonical dict ready for extraction.
    """
    if not SKILL_DICTIONARY_PATH.exists():
        raise FileNotFoundError(
            f"Skill dictionary not found: {SKILL_DICTIONARY_PATH}"
        )
    # load_skill_dictionary now accepts an optional path argument
    skill_df = load_skill_dictionary(str(SKILL_DICTIONARY_PATH))
    return prepare_skill_dictionary(skill_df)


# =========================================================
# LOAD SEMANTIC MODEL (once per process, cached)
# =========================================================

_SEMANTIC_MODEL = None  # module-level cache


def get_semantic_model():
    """
    Return a cached SentenceTransformer instance, or None if
    the dependency is unavailable.
    """
    global _SEMANTIC_MODEL
    if _SEMANTIC_MODEL is not None:
        return _SEMANTIC_MODEL
    try:
        from sentence_transformers import SentenceTransformer
        _SEMANTIC_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        return _SEMANTIC_MODEL
    except Exception:
        return None


# =========================================================
# SEMANTIC SIMILARITY
# =========================================================

def calculate_semantic_similarity(
    resume_text: str,
    job_text: str,
    model=None,
) -> float:
    """
    Cosine similarity via Sentence Transformers.
    Falls back to a simple token-overlap (TF-IDF-like) score
    when the model is unavailable.
    """
    if not resume_text.strip() or not job_text.strip():
        return 0.0

    if model is not None:
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            r_emb = model.encode([resume_text])
            j_emb = model.encode([job_text])
            score = float(cosine_similarity(r_emb, j_emb)[0][0])
            return max(0.0, score)
        except Exception:
            pass  # fall through to lexical fallback

    # --- Lexical fallback (token overlap Jaccard) ---
    r_tokens = set(resume_text.lower().split())
    j_tokens = set(job_text.lower().split())
    if not j_tokens:
        return 0.0
    overlap = r_tokens & j_tokens
    return len(overlap) / len(j_tokens | r_tokens)


# =========================================================
# BUILD TEXT REPRESENTATIONS
# =========================================================

def build_job_text(job: pd.Series) -> str:
    parts = [
        str(job.get("job_title", "")),
        str(job.get("domain", "")),
        str(job.get("required_skills", "")),
        str(job.get("education_required", "")),
        str(job.get("responsibilities", "")),
    ]
    return " ".join(p for p in parts if p.strip())


def build_resume_text(profile: dict) -> str:
    keys = [
        "summary", "skills_text", "skills",
        "education", "experience",
        "projects", "certifications", "achievements",
    ]
    parts = [str(profile.get(k, "") or "") for k in keys]
    # also include raw_text as final fallback
    raw = str(profile.get("raw_text", "") or "")
    if raw:
        parts.append(raw)
    return " ".join(p for p in parts if p.strip())


# =========================================================
# SKILL EXTRACTION FROM PROFILE
# =========================================================

def extract_resume_skills(
    profile: dict,
    skill_mapping: Dict[str, str],
) -> List[str]:
    """Collect all skills mentioned anywhere in the resume."""
    all_skills: set = set()

    # skills section (may be labelled "skills" or "skills_text")
    for key in ("skills_text", "skills"):
        text = profile.get(key, "") or ""
        if text:
            all_skills.update(extract_skills_from_list(text, skill_mapping))

    # free-text sections
    for key in ("raw_text", "projects", "experience", "summary", "certifications"):
        text = profile.get(key, "") or ""
        if text:
            all_skills.update(extract_skills(text, skill_mapping))

    return sorted(all_skills)


def extract_project_skills(
    profile: dict,
    skill_mapping: Dict[str, str],
) -> List[str]:
    text = profile.get("projects", "") or ""
    if not text:
        return []
    return sorted(set(extract_skills(text, skill_mapping)))


# =========================================================
# MATCHING HELPERS
# =========================================================

def calculate_skill_match(
    resume_skills: List[str],
    job_skills: List[str],
) -> Tuple[float, List[str], List[str]]:
    resume_set = {s.lower().strip() for s in resume_skills if s}
    job_set    = {s.lower().strip() for s in job_skills    if s}

    if not job_set:
        return 0.0, [], []

    matched_lower = resume_set & job_set
    missing_lower = job_set - resume_set

    # Restore original capitalisation from job list
    lookup = {s.lower(): s for s in job_skills}
    matched = [lookup[s] for s in sorted(matched_lower) if s in lookup]
    missing = [lookup[s] for s in sorted(missing_lower) if s in lookup]

    score = len(matched_lower) / len(job_set)
    return round(score, 4), matched, missing


def calculate_education_match(education: str, required: str) -> float:
    education = (education or "").lower()
    required  = (required  or "").lower()
    if not required.strip():
        return 1.0
    if not education.strip():
        return 0.0
    if required in education:
        return 1.0
    related = [
        "data science", "computer science", "information technology",
        "artificial intelligence", "machine learning", "statistics",
        "mathematics", "engineering",
    ]
    if any(t in required for t in related) and any(t in education for t in related):
        return 0.8
    return 0.4


def calculate_experience_match(candidate_years, required_years) -> float:
    try:
        cy = float(candidate_years or 0)
    except (ValueError, TypeError):
        cy = 0.0
    try:
        ry = float(required_years or 0)
    except (ValueError, TypeError):
        ry = 0.0
    if ry <= 0:
        return 1.0
    if cy >= ry:
        return 1.0
    if cy > 0:
        return round(cy / ry, 4)
    return 0.5


def calculate_project_relevance(
    project_skills: List[str],
    matched_skills: List[str],
) -> float:
    if not project_skills:
        return 0.0
    proj  = {s.lower() for s in project_skills}
    match = {s.lower() for s in matched_skills}
    overlap = proj & match
    return round(len(overlap) / len(proj), 4)


def calculate_hybrid_score(
    skill: float,
    semantic: float,
    project: float,
    education: float,
    experience: float,
) -> float:
    return round(
        skill * 0.40
        + semantic * 0.30
        + project  * 0.10
        + education * 0.10
        + experience * 0.10,
        4,
    )


def classify_match(score: float) -> str:
    pct = score * 100
    if pct >= 80:  return "Excellent Match"
    if pct >= 70:  return "Strong Match"
    if pct >= 55:  return "Moderate Match"
    if pct >= 40:  return "Weak Match"
    return "Low Match"


# =========================================================
# ANALYZE ONE JOB
# =========================================================

def analyze_job(
    profile: dict,
    resume_skills: List[str],
    project_skills: List[str],
    job: pd.Series,
    skill_mapping: Dict[str, str],
    semantic_model=None,
) -> dict:
    # Job skills
    job_skills = extract_skills_from_list(
        str(job.get("required_skills", "") or ""),
        skill_mapping,
    )

    skill_score, matched_skills, missing_skills = calculate_skill_match(
        resume_skills, job_skills
    )

    resume_text = build_resume_text(profile)
    job_text    = build_job_text(job)
    semantic_score = calculate_semantic_similarity(resume_text, job_text, semantic_model)

    project_score  = calculate_project_relevance(project_skills, matched_skills)
    education_score = calculate_education_match(
        profile.get("education", ""),
        str(job.get("education_required", "") or ""),
    )
    experience_score = calculate_experience_match(
        profile.get("experience_years", 0),
        job.get("experience_required_years", 0),
    )

    final_score    = calculate_hybrid_score(
        skill_score, semantic_score, project_score,
        education_score, experience_score,
    )
    classification = classify_match(final_score)

    return {
        "job_id":    str(job.get("job_id",    "") or ""),
        "job_title": str(job.get("job_title", "") or ""),
        "domain":    str(job.get("domain",    "") or ""),

        "skill_match_score":          skill_score,
        "semantic_similarity_score":  round(semantic_score, 4),
        "project_relevance_score":    project_score,
        "education_match_score":      round(education_score, 4),
        "experience_match_score":     experience_score,
        "final_match_score":          final_score,

        # match_percentage is what the frontend reads
        "match_percentage":           round(final_score * 100, 2),
        "classification":             classification,
        "match_classification":       classification,   # kept for compat

        # store as LISTS — the skill-gap loop needs them as lists
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
    }


# =========================================================
# MAIN ENTRY POINT
# =========================================================

def analyze_resume(resume_input) -> dict:
    """
    Complete resume analysis pipeline.

    Parameters
    ----------
    resume_input : dict | Path | str
        • dict  — already-parsed profile from parse_resume()   ← primary path
        • Path  — path to a PDF/DOCX file
        • str   — raw resume text or file path string

    Returns
    -------
    dict
        Frontend-ready flat object produced by build_clean_response().
    """

    # ----------------------------------------------------------
    # 1. Normalise input → profile dict
    # ----------------------------------------------------------
    if isinstance(resume_input, dict):
        # Use the pre-parsed dict directly — do NOT re-parse from
        # raw_text; that would throw away section-level information
        # the parser already extracted.
        profile = dict(resume_input)
    elif isinstance(resume_input, Path):
        from backend.parsers.resume_parser import parse_resume
        profile = parse_resume(resume_input)
    elif isinstance(resume_input, str):
        from backend.parsers.resume_parser import parse_resume
        profile = parse_resume(resume_input)
    else:
        raise TypeError(
            f"analyze_resume() expects dict, Path, or str; got {type(resume_input)}"
        )

    # Ensure all expected keys exist with safe defaults
    profile = _ensure_profile_defaults(profile)

    raw_text = profile.get("raw_text", "") or ""
    if not raw_text.strip():
        # Attempt to rebuild raw_text from sections
        raw_text = build_resume_text(profile)
    if not raw_text.strip():
        raise ValueError("No readable text found in resume.")

    # ----------------------------------------------------------
    # 2. Load resources (skills + jobs + semantic model)
    # ----------------------------------------------------------
    skill_mapping   = load_skills()
    jobs_df         = load_jobs()
    semantic_model  = get_semantic_model()  # None if unavailable → lexical fallback

    # ----------------------------------------------------------
    # 3. Extract skills from resume
    # ----------------------------------------------------------
    resume_skills  = extract_resume_skills(profile, skill_mapping)
    project_skills = extract_project_skills(profile, skill_mapping)

    # ----------------------------------------------------------
    # 4. Analyze every job
    # ----------------------------------------------------------
    job_results: List[dict] = []

    for _, job_row in jobs_df.iterrows():
        try:
            result = analyze_job(
                profile,
                resume_skills,
                project_skills,
                job_row,
                skill_mapping,
                semantic_model,
            )
            job_results.append(result)
        except Exception as exc:
            # One bad record must not kill the whole pipeline
            print(f"[analyzer] Skipping job {job_row.get('job_id', '?')}: {exc}")

    # ----------------------------------------------------------
    # 5. Rank
    # ----------------------------------------------------------
    job_results.sort(key=lambda x: x["final_match_score"], reverse=True)
    for rank, r in enumerate(job_results, start=1):
        r["rank"] = rank

    # ----------------------------------------------------------
    # 6. Top-job overall score & classification
    # ----------------------------------------------------------
    if job_results:
        top = job_results[0]
        overall_score    = top["match_percentage"]
        classification   = top["classification"]
        # Aggregate matched/missing from top-5 for the skills card
        top_matched: set = set()
        top_missing: set = set()
        for r in job_results[:5]:
            top_matched.update(r["matched_skills"])
            top_missing.update(r["missing_skills"])
        # missing only if not matched by resume at all
        top_missing -= top_matched
    else:
        overall_score  = 0.0
        classification = "No Match"
        top_matched    = set(resume_skills)
        top_missing    = set()

    # ----------------------------------------------------------
    # 7. Skill gap aggregation (missing skill → frequency count)
    # ----------------------------------------------------------
    gap_counter: Dict[str, int] = {}
    for r in job_results:
        for skill in r["missing_skills"]:  # already a list
            skill = skill.strip()
            if skill:
                gap_counter[skill] = gap_counter.get(skill, 0) + 1

    skill_gaps = sorted(
        [{"skill": s, "importance": c / max(len(job_results), 1)}
         for s, c in gap_counter.items()],
        key=lambda x: x["importance"],
        reverse=True,
    )

    # ----------------------------------------------------------
    # 8. Learning recommendations (top unique missing skills)
    # ----------------------------------------------------------
    learning_recommendations = [
        {
            "skill": gap["skill"],
            "reason": (
                f"This skill appears in "
                f"{int(gap['importance'] * len(job_results))} "
                f"of the matched jobs. Adding it to your profile "
                f"will improve your overall match score."
            ),
        }
        for gap in skill_gaps[:10]
    ]

    # ----------------------------------------------------------
    # 9. Build raw result dict and pass through response formatter
    # ----------------------------------------------------------
    candidate_name = (
        profile.get("name")
        or profile.get("candidate_name")
        or "Candidate"
    )

    raw_result = {
        # candidate block expected by build_clean_response
        "candidate": {
            "name":       candidate_name,
            "education":  profile.get("education", ""),
            "experience": profile.get("experience_years", 0),
        },

        "overall_score":  overall_score,
        "classification": classification,

        # skills block expected by build_clean_response
        "skills": {
            "matched": sorted(top_matched),
            "missing": sorted(top_missing),
        },

        "job_recommendations":     job_results,
        "skill_gaps":              skill_gaps,
        "learning_recommendations": learning_recommendations,
    }

    # build_clean_response converts to the exact shape the
    # React components expect (safe types, consistent keys).
    return build_clean_response(raw_result)


# =========================================================
# INTERNAL HELPER
# =========================================================

def _ensure_profile_defaults(profile: dict) -> dict:
    """Fill any missing keys with safe empty defaults."""
    defaults = {
        "name":             "Candidate",
        "candidate_name":   "Candidate",
        "raw_text":         "",
        "summary":          "",
        "education":        "",
        "experience":       "",
        "skills":           "",
        "skills_text":      "",
        "projects":         "",
        "certifications":   "",
        "achievements":     "",
        "interests":        "",
        "soft_skills":      "",
        "other":            "",
        "experience_years": 0,
    }
    for key, default in defaults.items():
        if key not in profile or profile[key] is None:
            profile[key] = default

    # Normalise experience_years to float
    try:
        profile["experience_years"] = float(profile["experience_years"])
    except (ValueError, TypeError):
        profile["experience_years"] = 0.0

    # skills_text alias — parser stores section as "skills"
    if not profile.get("skills_text") and profile.get("skills"):
        profile["skills_text"] = profile["skills"]

    return profile
