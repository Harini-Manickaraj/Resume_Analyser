from pathlib import Path
import ast
import pandas as pd


# ============================================================
# PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DATA_DIR = PROJECT_ROOT / "data" / "datasets"
PROCESSED_DIR = DATA_DIR / "processed"

RESUME_FILE = DATA_DIR / "resume_profiles.csv"
JOB_FILE = DATA_DIR / "job_descriptions.csv"
SKILL_MATCH_FILE = PROCESSED_DIR / "skill_match_results.csv"
SEMANTIC_FILE = PROCESSED_DIR / "semantic_similarity_results.csv"

OUTPUT_FILE = PROCESSED_DIR / "hybrid_matching_results.csv"


# ============================================================
# WEIGHTS
# ============================================================

SKILL_WEIGHT = 0.40
SEMANTIC_WEIGHT = 0.30
PROJECT_WEIGHT = 0.10
EDUCATION_WEIGHT = 0.10
EXPERIENCE_WEIGHT = 0.10


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def safe_string(value):
    """
    Convert a value into a safe lowercase string.
    """
    if pd.isna(value):
        return ""

    return str(value).strip()


def parse_skill_list(value):
    """
    Convert semicolon-separated or Python-list-like text
    into a clean list of skills.
    """

    if pd.isna(value):
        return []

    text = str(value).strip()

    if not text:
        return []

    # Try parsing Python-list representation
    if text.startswith("[") and text.endswith("]"):
        try:
            parsed = ast.literal_eval(text)

            if isinstance(parsed, list):
                return [
                    str(item).strip()
                    for item in parsed
                    if str(item).strip()
                ]
        except (ValueError, SyntaxError):
            pass

    # Standard semicolon-separated format
    if ";" in text:
        return [
            item.strip()
            for item in text.split(";")
            if item.strip()
        ]

    # Comma-separated fallback
    if "," in text:
        return [
            item.strip()
            for item in text.split(",")
            if item.strip()
        ]

    return [text]


def normalize_skill_text(skill):
    """
    Normalize skill text for comparison.
    """
    return (
        safe_string(skill)
        .lower()
        .replace("-", " ")
        .replace("_", " ")
    )


# ============================================================
# EDUCATION MATCHING
# ============================================================

def calculate_education_match(resume_education, job_education):
    """
    Calculate education compatibility.

    Returns:
        1.0  -> strong match
        0.5  -> partial/related match
        0.0  -> no clear match
    """

    resume_education = normalize_skill_text(resume_education)
    job_education = normalize_skill_text(job_education)

    if not job_education:
        return 1.0

    if not resume_education:
        return 0.0

    # Exact / direct keyword matching
    education_keywords = [
        "data science",
        "computer science",
        "information technology",
        "artificial intelligence",
        "machine learning",
        "software engineering",
        "engineering",
        "statistics",
        "mathematics",
        "business analytics",
        "analytics",
    ]

    resume_matches = [
        keyword
        for keyword in education_keywords
        if keyword in resume_education
    ]

    job_matches = [
        keyword
        for keyword in education_keywords
        if keyword in job_education
    ]

    if not job_matches:
        return 0.5

    if any(keyword in resume_education for keyword in job_matches):
        return 1.0

    # Related technical education
    if (
        "degree" in job_education
        or "bachelor" in job_education
        or "master" in job_education
        or "m.sc" in job_education
        or "mca" in job_education
        or "b.tech" in job_education
        or "b.e" in job_education
    ):
        if resume_matches:
            return 0.5

    return 0.0


# ============================================================
# EXPERIENCE MATCHING
# ============================================================

def calculate_experience_match(
    resume_experience,
    required_experience
):
    """
    Calculate experience compatibility.

    Returns a score between 0 and 1.
    """

    try:
        resume_experience = float(resume_experience)
    except (ValueError, TypeError):
        resume_experience = 0.0

    try:
        required_experience = float(required_experience)
    except (ValueError, TypeError):
        required_experience = 0.0

    # No experience required
    if required_experience <= 0:
        return 1.0

    # Candidate meets or exceeds requirement
    if resume_experience >= required_experience:
        return 1.0

    # Partial experience
    if resume_experience > 0:
        return min(
            resume_experience / required_experience,
            1.0
        )

    # Internship / fresher candidate
    return 0.5


# ============================================================
# PROJECT RELEVANCE
# ============================================================

def calculate_project_relevance(
    resume_project_skills,
    matched_skills,
    required_skills
):
    """
    Calculate how strongly the candidate's projects relate
    to the job requirements.

    Score:
        0.0 -> no project relevance
        1.0 -> strong project relevance
    """

    project_skills = parse_skill_list(resume_project_skills)
    matched = parse_skill_list(matched_skills)
    required = parse_skill_list(required_skills)

    if not required:
        return 0.0

    project_text = " ".join(
        normalize_skill_text(skill)
        for skill in project_skills
    )

    if not project_text:
        return 0.0

    relevant_count = 0

    for skill in required:
        normalized_skill = normalize_skill_text(skill)

        if not normalized_skill:
            continue

        # Direct project skill match
        if normalized_skill in project_text:
            relevant_count += 1
            continue

        # Check matched skills
        for matched_skill in matched:
            normalized_matched = normalize_skill_text(
                matched_skill
            )

            if (
                normalized_skill in normalized_matched
                or normalized_matched in normalized_skill
            ):
                relevant_count += 1
                break

    score = relevant_count / len(required)

    return min(score, 1.0)


# ============================================================
# SCORE NORMALIZATION
# ============================================================

def normalize_score(value):
    """
    Make sure a score is between 0 and 1.
    """

    try:
        value = float(value)
    except (ValueError, TypeError):
        return 0.0

    # Handle percentage values
    if value > 1:
        value = value / 100

    return max(0.0, min(value, 1.0))


# ============================================================
# MATCH CLASSIFICATION
# ============================================================

def classify_match(score):
    """
    Convert numerical score into a human-readable class.
    """

    percentage = score * 100

    if percentage >= 80:
        return "Excellent Match"

    if percentage >= 70:
        return "Strong Match"

    if percentage >= 55:
        return "Moderate Match"

    if percentage >= 40:
        return "Weak Match"

    return "Low Match"


# ============================================================
# EXPLANATION GENERATION
# ============================================================

def generate_explanation(
    final_score,
    matched_skills,
    missing_skills,
    project_score,
    education_score,
    experience_score
):
    """
    Generate a simple explainable reason for the match.
    """

    explanation_parts = []

    matched = parse_skill_list(matched_skills)
    missing = parse_skill_list(missing_skills)

    if matched:
        matched_text = ", ".join(matched[:5])
        explanation_parts.append(
            f"Matched skills: {matched_text}"
        )

    if missing:
        missing_text = ", ".join(missing[:5])
        explanation_parts.append(
            f"Skill gaps: {missing_text}"
        )

    if project_score >= 0.7:
        explanation_parts.append(
            "Projects show strong relevance to the job."
        )
    elif project_score >= 0.4:
        explanation_parts.append(
            "Projects show moderate relevance to the job."
        )
    else:
        explanation_parts.append(
            "Limited direct project relevance."
        )

    if education_score >= 1.0:
        explanation_parts.append(
            "Education aligns well with the role."
        )
    elif education_score >= 0.5:
        explanation_parts.append(
            "Education is partially related to the role."
        )
    else:
        explanation_parts.append(
            "Education does not clearly match the stated requirement."
        )

    if experience_score >= 1.0:
        explanation_parts.append(
            "Experience requirement is satisfied."
        )
    elif experience_score >= 0.5:
        explanation_parts.append(
            "Experience provides partial alignment."
        )
    else:
        explanation_parts.append(
            "Experience requirement is not fully satisfied."
        )

    return " ".join(explanation_parts)


# ============================================================
# LOAD DATA
# ============================================================

def load_data():
    """
    Load all required datasets.
    """

    print("=" * 60)
    print("LOADING DATA")
    print("=" * 60)

    if not RESUME_FILE.exists():
        raise FileNotFoundError(
            f"Resume dataset not found: {RESUME_FILE}"
        )

    if not JOB_FILE.exists():
        raise FileNotFoundError(
            f"Job dataset not found: {JOB_FILE}"
        )

    if not SKILL_MATCH_FILE.exists():
        raise FileNotFoundError(
            f"Skill matching file not found: {SKILL_MATCH_FILE}"
        )

    if not SEMANTIC_FILE.exists():
        raise FileNotFoundError(
            f"Semantic similarity file not found: {SEMANTIC_FILE}"
        )

    resumes = pd.read_csv(RESUME_FILE)
    jobs = pd.read_csv(JOB_FILE)
    skill_matches = pd.read_csv(SKILL_MATCH_FILE)
    semantic_results = pd.read_csv(SEMANTIC_FILE)

    print(f"Resumes loaded: {len(resumes)}")
    print(f"Jobs loaded: {len(jobs)}")
    print(f"Skill match records: {len(skill_matches)}")
    print(f"Semantic records: {len(semantic_results)}")

    return (
        resumes,
        jobs,
        skill_matches,
        semantic_results
    )


# ============================================================
# SEMANTIC SCORE LOOKUP
# ============================================================

def create_semantic_lookup(semantic_results):
    """
    Create dictionary:

        (candidate_id, job_id) -> semantic similarity
    """

    semantic_lookup = {}

    for _, row in semantic_results.iterrows():

        candidate_id = safe_string(
            row.get("candidate_id", "")
        )

        job_id = safe_string(
            row.get("job_id", "")
        )

        score = row.get(
            "semantic_similarity",
            row.get(
                "semantic_similarity_score",
                row.get("similarity", 0)
            )
        )

        score = normalize_score(score)

        semantic_lookup[
            (candidate_id, job_id)
        ] = score

    return semantic_lookup


# ============================================================
# MAIN HYBRID MATCHING ENGINE
# ============================================================

def run_hybrid_matching():

    print()
    print("=" * 60)
    print("HYBRID RESUME-JOB MATCHING ENGINE")
    print("=" * 60)

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    (
        resumes,
        jobs,
        skill_matches,
        semantic_results
    ) = load_data()

    semantic_lookup = create_semantic_lookup(
        semantic_results
    )

    results = []

    # --------------------------------------------------------
    # Process each candidate
    # --------------------------------------------------------

    for _, resume in resumes.iterrows():

        candidate_id = safe_string(
            resume.get("candidate_id", "")
        )

        print()
        print(f"Processing candidate: {candidate_id}")

        candidate_matches = skill_matches[
            skill_matches["candidate_id"].astype(str)
            == candidate_id
        ]

        # ----------------------------------------------------
        # Process every job
        # ----------------------------------------------------

        for _, job in jobs.iterrows():

            job_id = safe_string(
                job.get("job_id", "")
            )

            job_title = safe_string(
                job.get("job_title", "")
            )

            # ------------------------------------------------
            # Find skill-match record
            # ------------------------------------------------

            matching_rows = candidate_matches[
                candidate_matches["job_id"].astype(str)
                == job_id
            ]

            if len(matching_rows) > 0:
                match_row = matching_rows.iloc[0]
            else:
                match_row = pd.Series()

            # ------------------------------------------------
            # Skill score
            # ------------------------------------------------

            skill_score = normalize_score(
                match_row.get(
                    "skill_match_percentage",
                    match_row.get(
                        "skill_match_score",
                        match_row.get(
                            "skill_overlap_score",
                            0
                        )
                    )
                )
            )

            # ------------------------------------------------
            # Matched / missing skills
            # ------------------------------------------------

            matched_skills = safe_string(
                match_row.get(
                    "matched_skills",
                    ""
                )
            )

            missing_skills = safe_string(
                match_row.get(
                    "missing_skills",
                    ""
                )
            )

            # ------------------------------------------------
            # Semantic similarity
            # ------------------------------------------------

            semantic_score = semantic_lookup.get(
                (candidate_id, job_id),
                0.0
            )

            # ------------------------------------------------
            # Project relevance
            # ------------------------------------------------

            project_score = calculate_project_relevance(
                resume.get("project_skills", ""),
                matched_skills,
                job.get("required_skills", "")
            )

            # ------------------------------------------------
            # Education match
            # ------------------------------------------------

            education_score = calculate_education_match(
                resume.get("education", ""),
                job.get("education_required", "")
            )

            # ------------------------------------------------
            # Experience match
            # ------------------------------------------------

            experience_score = calculate_experience_match(
                resume.get("experience_years", 0),
                job.get(
                    "experience_required_years",
                    0
                )
            )

            # ------------------------------------------------
            # HYBRID FINAL SCORE
            # ------------------------------------------------

            final_score = (
                (skill_score * SKILL_WEIGHT)
                + (semantic_score * SEMANTIC_WEIGHT)
                + (project_score * PROJECT_WEIGHT)
                + (education_score * EDUCATION_WEIGHT)
                + (experience_score * EXPERIENCE_WEIGHT)
            )

            final_score = max(
                0.0,
                min(final_score, 1.0)
            )

            # ------------------------------------------------
            # Classification
            # ------------------------------------------------

            classification = classify_match(
                final_score
            )

            # ------------------------------------------------
            # Explanation
            # ------------------------------------------------

            explanation = generate_explanation(
                final_score,
                matched_skills,
                missing_skills,
                project_score,
                education_score,
                experience_score
            )

            # ------------------------------------------------
            # Store result
            # ------------------------------------------------

            results.append({
                "candidate_id": candidate_id,
                "job_id": job_id,
                "job_title": job_title,

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

                "final_match_score": round(
                    final_score,
                    4
                ),

                "match_percentage": round(
                    final_score * 100,
                    2
                ),

                "match_classification": classification,

                "matched_skills": matched_skills,

                "missing_skills": missing_skills,

                "explanation": explanation
            })

    # ========================================================
    # CREATE DATAFRAME
    # ========================================================

    results_df = pd.DataFrame(results)

    # ========================================================
    # SORT RESULTS
    # ========================================================

    results_df = results_df.sort_values(
        by=[
            "candidate_id",
            "final_match_score"
        ],
        ascending=[
            True,
            False
        ]
    ).reset_index(drop=True)

    # ========================================================
    # CREATE OUTPUT DIRECTORY
    # ========================================================

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # ========================================================
    # SAVE OUTPUT
    # ========================================================

    results_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # ========================================================
    # DISPLAY RESULTS
    # ========================================================

    print()
    print("=" * 60)
    print("HYBRID MATCHING COMPLETED")
    print("=" * 60)

    print(
        f"Total matching records: {len(results_df)}"
    )

    print(
        f"Output saved to:\n{OUTPUT_FILE}"
    )

    print()
    print("=" * 60)
    print("TOP JOB RECOMMENDATIONS")
    print("=" * 60)

    display_columns = [
        "job_id",
        "job_title",
        "match_percentage",
        "match_classification"
    ]

    print(
        results_df[
            display_columns
        ].head(10).to_string(index=False)
    )

    print()
    print("=" * 60)
    print("HYBRID SCORE WEIGHTS")
    print("=" * 60)

    print(
        f"Skill Match       : {SKILL_WEIGHT * 100:.0f}%"
    )

    print(
        f"Semantic Similarity: {SEMANTIC_WEIGHT * 100:.0f}%"
    )

    print(
        f"Project Relevance : {PROJECT_WEIGHT * 100:.0f}%"
    )

    print(
        f"Education Match   : {EDUCATION_WEIGHT * 100:.0f}%"
    )

    print(
        f"Experience Match  : {EXPERIENCE_WEIGHT * 100:.0f}%"
    )

    return results_df


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_hybrid_matching()