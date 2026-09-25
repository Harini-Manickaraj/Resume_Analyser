from pathlib import Path
from typing import Dict, List

import pandas as pd

from backend.parsers.resume_parser import (
    extract_resume_text,
    create_resume_profile
)

from backend.nlp.skill_extraction import (
    load_skill_dictionary,
    extract_skills,
    extract_skills_from_list
)


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = (
    Path(__file__).resolve().parent.parent.parent
)

DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "datasets"
)

SKILL_DICTIONARY_PATH = (
    DATA_DIR
    / "skill_dictionary.csv"
)

JOB_DATASET_PATH = (
    DATA_DIR
    / "job_descriptions.csv"
)


# =========================================================
# LOAD JOB DATASET
# =========================================================

def load_jobs() -> pd.DataFrame:
    """
    Load the available job descriptions.
    """

    if not JOB_DATASET_PATH.exists():

        raise FileNotFoundError(
            "Job description dataset not found."
        )

    jobs = pd.read_csv(
        JOB_DATASET_PATH
    )

    return jobs.fillna("")


# =========================================================
# LOAD SKILL DICTIONARY
# =========================================================

def load_skills() -> Dict[str, str]:
    """
    Load canonical skill mapping.

    Returns:
        dictionary mapping aliases to canonical skills.
    """

    if not SKILL_DICTIONARY_PATH.exists():

        raise FileNotFoundError(
            "Skill dictionary not found."
        )

    return load_skill_dictionary(
        str(SKILL_DICTIONARY_PATH)
    )


# =========================================================
# EXTRACT RESUME SKILLS
# =========================================================

def extract_resume_skills(
    profile: dict,
    skill_mapping: Dict[str, str]
) -> List[str]:
    """
    Extract normalized skills from the uploaded resume.
    """

    all_skills = set()

    # -----------------------------------------------------
    # Skills section
    # -----------------------------------------------------

    skills_text = profile.get(
        "skills_text",
        ""
    )

    if skills_text:

        skills = extract_skills_from_list(
            skills_text,
            skill_mapping
        )

        all_skills.update(
            skills
        )

    # -----------------------------------------------------
    # Entire resume
    # -----------------------------------------------------

    raw_text = profile.get(
        "raw_text",
        ""
    )

    if raw_text:

        skills = extract_skills(
            raw_text,
            skill_mapping
        )

        all_skills.update(
            skills
        )

    # -----------------------------------------------------
    # Projects
    # -----------------------------------------------------

    projects = profile.get(
        "projects",
        ""
    )

    if projects:

        skills = extract_skills(
            projects,
            skill_mapping
        )

        all_skills.update(
            skills
        )

    # -----------------------------------------------------
    # Experience
    # -----------------------------------------------------

    experience = profile.get(
        "experience",
        ""
    )

    if experience:

        skills = extract_skills(
            experience,
            skill_mapping
        )

        all_skills.update(
            skills
        )

    return sorted(
        all_skills
    )


# =========================================================
# EXTRACT PROJECT SKILLS
# =========================================================

def extract_project_skills(
    profile: dict,
    skill_mapping: Dict[str, str]
) -> List[str]:
    """
    Extract skills specifically from projects.
    """

    projects = profile.get(
        "projects",
        ""
    )

    if not projects:

        return []

    skills = extract_skills(
        projects,
        skill_mapping
    )

    return sorted(
        set(skills)
    )


# =========================================================
# CALCULATE SKILL MATCH
# =========================================================

def calculate_skill_match(
    resume_skills: List[str],
    job_skills: List[str]
):
    """
    Calculate skill overlap between resume and job.
    """

    resume_set = {
        skill.lower().strip()
        for skill in resume_skills
        if skill
    }

    job_set = {
        skill.lower().strip()
        for skill in job_skills
        if skill
    }

    if not job_set:

        return {
            "score": 0.0,
            "matched_skills": [],
            "missing_skills": []
        }

    matched = (
        resume_set
        & job_set
    )

    missing = (
        job_set
        - resume_set
    )

    score = (
        len(matched)
        / len(job_set)
    )

    # Recover original capitalization
    canonical_lookup = {
        skill.lower(): skill
        for skill in job_skills
    }

    matched_skills = [
        canonical_lookup[
            skill
        ]
        for skill in sorted(matched)
    ]

    missing_skills = [
        canonical_lookup[
            skill
        ]
        for skill in sorted(missing)
    ]

    return {
        "score": score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }


# =========================================================
# CALCULATE EDUCATION MATCH
# =========================================================

def calculate_education_match(
    education: str,
    required_education: str
) -> float:
    """
    Basic education compatibility score.
    """

    education = (
        education or ""
    ).lower()

    required_education = (
        required_education or ""
    ).lower()

    # No requirement
    if not required_education.strip():

        return 1.0

    # No candidate education
    if not education.strip():

        return 0.0

    # Direct match
    if required_education in education:

        return 1.0

    # Related data science / computer science fields
    related_terms = [
        "data science",
        "computer science",
        "information technology",
        "artificial intelligence",
        "machine learning",
        "statistics",
        "mathematics",
        "engineering"
    ]

    required_related = any(
        term in required_education
        for term in related_terms
    )

    candidate_related = any(
        term in education
        for term in related_terms
    )

    if (
        required_related
        and candidate_related
    ):

        return 0.8

    return 0.4


# =========================================================
# CALCULATE EXPERIENCE MATCH
# =========================================================

def calculate_experience_match(
    experience_years: float,
    required_years: float
) -> float:
    """
    Calculate experience compatibility.
    """

    try:

        candidate_years = float(
            experience_years
        )

    except (
        ValueError,
        TypeError
    ):

        candidate_years = 0.0

    try:

        required_years = float(
            required_years
        )

    except (
        ValueError,
        TypeError
    ):

        required_years = 0.0

    # No experience required
    if required_years <= 0:

        return 1.0

    # Candidate meets requirement
    if candidate_years >= required_years:

        return 1.0

    # Partial experience
    if candidate_years > 0:

        return (
            candidate_years
            / required_years
        )

    # Fresher
    return 0.5


# =========================================================
# SEMANTIC SIMILARITY
# =========================================================

def calculate_semantic_similarity(
    resume_text: str,
    job_text: str
) -> float:
    """
    Calculate semantic similarity using
    Sentence Transformers.
    """

    try:

        from sentence_transformers import (
            SentenceTransformer
        )

        from sklearn.metrics.pairwise import (
            cosine_similarity
        )

    except ImportError:

        raise ImportError(
            "Sentence Transformers and "
            "scikit-learn are required."
        )

    model = SentenceTransformer(
        "all-MiniLM-L6-v2"
    )

    resume_embedding = model.encode(
        [resume_text]
    )

    job_embedding = model.encode(
        [job_text]
    )

    similarity = cosine_similarity(
        resume_embedding,
        job_embedding
    )[0][0]

    # Cosine similarity can theoretically
    # be negative.
    similarity = max(
        0.0,
        float(similarity)
    )

    return similarity


# =========================================================
# BUILD JOB TEXT
# =========================================================

def build_job_text(
    job: pd.Series
) -> str:
    """
    Build textual representation of a job.
    """

    parts = [
        str(job.get(
            "job_title",
            ""
        )),

        str(job.get(
            "domain",
            ""
        )),

        str(job.get(
            "required_skills",
            ""
        )),

        str(job.get(
            "education_required",
            ""
        )),

        str(job.get(
            "responsibilities",
            ""
        ))
    ]

    return " ".join(
        part
        for part in parts
        if part.strip()
    )


# =========================================================
# BUILD RESUME TEXT
# =========================================================

def build_resume_text(
    profile: dict
) -> str:
    """
    Build textual representation of resume.
    """

    parts = [
        profile.get(
            "summary",
            ""
        ),

        profile.get(
            "skills_text",
            ""
        ),

        profile.get(
            "education",
            ""
        ),

        profile.get(
            "experience",
            ""
        ),

        profile.get(
            "projects",
            ""
        ),

        profile.get(
            "certifications",
            ""
        ),

        profile.get(
            "achievements",
            ""
        )
    ]

    return " ".join(
        str(part)
        for part in parts
        if str(part).strip()
    )


# =========================================================
# PROJECT RELEVANCE
# =========================================================

def calculate_project_relevance(
    project_skills: List[str],
    matched_skills: List[str]
) -> float:
    """
    Estimate how strongly the candidate's projects
    support the job requirements.
    """

    if not project_skills:

        return 0.0

    project_set = {
        skill.lower()
        for skill in project_skills
    }

    matched_set = {
        skill.lower()
        for skill in matched_skills
    }

    overlap = (
        project_set
        & matched_set
    )

    if not project_set:

        return 0.0

    return (
        len(overlap)
        / len(project_set)
    )


# =========================================================
# HYBRID SCORE
# =========================================================

def calculate_hybrid_score(
    skill_score: float,
    semantic_score: float,
    project_score: float,
    education_score: float,
    experience_score: float
) -> float:
    """
    Calculate final hybrid matching score.

    Weights:
        Skill       = 40%
        Semantic    = 30%
        Project     = 10%
        Education   = 10%
        Experience  = 10%
    """

    final_score = (

        skill_score * 0.40

        + semantic_score * 0.30

        + project_score * 0.10

        + education_score * 0.10

        + experience_score * 0.10
    )

    return round(
        final_score,
        4
    )


# =========================================================
# CLASSIFICATION
# =========================================================

def classify_match(
    score: float
) -> str:
    """
    Convert matching score into classification.
    """

    percentage = score * 100

    if percentage >= 80:

        return "Excellent Match"

    elif percentage >= 70:

        return "Strong Match"

    elif percentage >= 55:

        return "Moderate Match"

    elif percentage >= 40:

        return "Weak Match"

    return "Low Match"


# =========================================================
# EXPLANATION
# =========================================================

def create_explanation(
    classification: str,
    matched_skills: List[str],
    missing_skills: List[str]
) -> str:
    """
    Generate a human-readable explanation.
    """

    explanation = (
        f"{classification}. "
    )

    if matched_skills:

        explanation += (
            "The candidate matches "
            f"{len(matched_skills)} "
            "required skills. "
        )

    if missing_skills:

        explanation += (
            f"{len(missing_skills)} "
            "skills are missing."
        )

    else:

        explanation += (
            "All identified required skills "
            "are covered."
        )

    return explanation


# =========================================================
# ANALYZE ONE JOB
# =========================================================

def analyze_job(
    profile: dict,
    resume_skills: List[str],
    project_skills: List[str],
    job: pd.Series,
    skill_mapping: Dict[str, str]
) -> dict:
    """
    Analyze one resume against one job.
    """

    # -----------------------------------------------------
    # Job skills
    # -----------------------------------------------------

    required_skills_text = str(
        job.get(
            "required_skills",
            ""
        )
    )

    job_skills = extract_skills_from_list(
        required_skills_text,
        skill_mapping
    )

    # -----------------------------------------------------
    # Skill matching
    # -----------------------------------------------------

    skill_result = calculate_skill_match(
        resume_skills,
        job_skills
    )

    skill_score = skill_result[
        "score"
    ]

    matched_skills = skill_result[
        "matched_skills"
    ]

    missing_skills = skill_result[
        "missing_skills"
    ]

    # -----------------------------------------------------
    # Semantic matching
    # -----------------------------------------------------

    resume_text = build_resume_text(
        profile
    )

    job_text = build_job_text(
        job
    )

    semantic_score = calculate_semantic_similarity(
        resume_text,
        job_text
    )

    # -----------------------------------------------------
    # Project relevance
    # -----------------------------------------------------

    project_score = calculate_project_relevance(
        project_skills,
        matched_skills
    )

    # -----------------------------------------------------
    # Education
    # -----------------------------------------------------

    education_score = calculate_education_match(
        profile.get(
            "education",
            ""
        ),
        job.get(
            "education_required",
            ""
        )
    )

    # -----------------------------------------------------
    # Experience
    # -----------------------------------------------------

    experience_score = calculate_experience_match(
        0,
        job.get(
            "experience_required_years",
            0
        )
    )

    # -----------------------------------------------------
    # Final score
    # -----------------------------------------------------

    final_score = calculate_hybrid_score(
        skill_score,
        semantic_score,
        project_score,
        education_score,
        experience_score
    )

    classification = classify_match(
        final_score
    )

    explanation = create_explanation(
        classification,
        matched_skills,
        missing_skills
    )

    # -----------------------------------------------------
    # Result
    # -----------------------------------------------------

    return {

        "job_id": job.get(
            "job_id",
            ""
        ),

        "job_title": job.get(
            "job_title",
            ""
        ),

        "domain": job.get(
            "domain",
            ""
        ),

        "skill_match_score": round(
            skill_score,
            4
        ),

        "semantic_similarity_score": round(
            semantic_score,
            4
        ),

        "project_relevance_score": round(
            project_score,
            4
        ),

        "education_match_score": round(
            education_score,
            4
        ),

        "experience_match_score": round(
            experience_score,
            4
        ),

        "final_match_score": final_score,

        "match_percentage": round(
            final_score * 100,
            2
        ),

        "match_classification": (
            classification
        ),

        "matched_skills": (
            ", ".join(
                matched_skills
            )
        ),

        "missing_skills": (
            ", ".join(
                missing_skills
            )
        ),

        "explanation": explanation
    }


# =========================================================
# ANALYZE RESUME
# =========================================================

def analyze_resume(
    file_path: str
) -> dict:
    """
    Complete resume analysis pipeline.

    Input:
        PDF or DOCX resume

    Output:
        Resume profile
        Extracted skills
        Job recommendations
        Skill gaps
    """

    # -----------------------------------------------------
    # Extract text
    # -----------------------------------------------------

    resume_text = extract_resume_text(
        file_path
    )

    if not resume_text.strip():

        raise ValueError(
            "No readable text found in resume."
        )

    # -----------------------------------------------------
    # Create profile
    # -----------------------------------------------------

    profile = create_resume_profile(
        resume_text
    )

    # -----------------------------------------------------
    # Load skills
    # -----------------------------------------------------

    skill_mapping = load_skills()

    # -----------------------------------------------------
    # Extract skills
    # -----------------------------------------------------

    resume_skills = extract_resume_skills(
        profile,
        skill_mapping
    )

    project_skills = extract_project_skills(
        profile,
        skill_mapping
    )

    # -----------------------------------------------------
    # Load jobs
    # -----------------------------------------------------

    jobs = load_jobs()

    # -----------------------------------------------------
    # Analyze every job
    # -----------------------------------------------------

    results = []

    for _, job in jobs.iterrows():

        try:

            result = analyze_job(
                profile,
                resume_skills,
                project_skills,
                job,
                skill_mapping
            )

            results.append(
                result
            )

        except Exception as e:

            print(
                f"Warning: Could not analyze "
                f"{job.get('job_id', '')}: {e}"
            )

    # -----------------------------------------------------
    # Sort
    # -----------------------------------------------------

    results.sort(
        key=lambda x: x[
            "final_match_score"
        ],
        reverse=True
    )

    # -----------------------------------------------------
    # Add ranking
    # -----------------------------------------------------

    for index, result in enumerate(
        results,
        start=1
    ):

        result[
            "rank"
        ] = index

    # -----------------------------------------------------
    # Skill gap summary
    # -----------------------------------------------------

    all_missing_skills = {}

    for result in results:

        missing = (
            result["missing_skills"]
            .split(",")
        )

        for skill in missing:

            skill = skill.strip()

            if not skill:
                continue

            all_missing_skills[
                skill
            ] = (
                all_missing_skills.get(
                    skill,
                    0
                ) + 1
            )

    # -----------------------------------------------------
    # Sort skill gaps by frequency
    # -----------------------------------------------------

    skill_gaps = sorted(
        [
            {
                "skill": skill,
                "job_count": count
            }

            for skill, count
            in all_missing_skills.items()
        ],

        key=lambda x: x[
            "job_count"
        ],

        reverse=True
    )

    # -----------------------------------------------------
    # Resume result
    # -----------------------------------------------------

    return {

        "resume": profile,

        "extracted_skills": resume_skills,

        "project_skills": project_skills,

        "job_recommendations": results,

        "skill_gaps": skill_gaps
    }


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("=" * 70)
    print("DYNAMIC RESUME ANALYZER")
    print("=" * 70)

    print()
    print(
        "This module analyzes an uploaded resume "
        "against all available jobs."
    )

    print()
    print(
        "Usage:"
    )

    print(
        "analyze_resume('path/to/resume.pdf')"
    )