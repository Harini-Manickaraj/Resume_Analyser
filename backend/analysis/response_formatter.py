from typing import Any


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert a value to float."""

    try:
        if value is None:
            return default

        return round(float(value), 2)

    except (ValueError, TypeError):
        return default


def safe_list(value: Any) -> list:
    """Convert common values into a clean list."""

    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, tuple):
        return list(value)

    if isinstance(value, set):
        return list(value)

    if isinstance(value, str):

        if not value.strip():
            return []

        # Handle comma/semicolon separated values
        items = value.replace(";", ",").split(",")

        return [
            item.strip()
            for item in items
            if item.strip()
        ]

    return []


def clean_skill_list(value: Any) -> list:
    """Clean and remove duplicate skills."""

    skills = safe_list(value)

    cleaned = []
    seen = set()

    for skill in skills:

        if not isinstance(skill, str):
            continue

        skill = skill.strip()

        if not skill:
            continue

        key = skill.lower()

        if key not in seen:
            seen.add(key)
            cleaned.append(skill)

    return cleaned


def format_job_recommendations(recommendations: Any) -> list:
    """Format recommended jobs for the frontend."""

    if recommendations is None:
        return []

    if hasattr(recommendations, "to_dict"):
        try:
            recommendations = recommendations.to_dict(
                orient="records"
            )
        except Exception:
            return []

    if not isinstance(recommendations, list):
        return []

    formatted = []

    for job in recommendations:

        if not isinstance(job, dict):
            continue

        formatted.append({
            "job_id": job.get(
                "job_id",
                job.get("id", "")
            ),

            "job_title": job.get(
                "job_title",
                job.get("title", "")
            ),

            "match_percentage": safe_float(
                job.get(
                    "match_percentage",
                    job.get(
                        "final_match_score",
                        job.get("score", 0)
                    )
                )
            ),

            "classification": job.get(
                "classification",
                job.get(
                    "match_classification",
                    ""
                )
            )
        })

    return formatted


def format_skill_gaps(skill_gaps: Any) -> list:
    """Format skill gap information."""

    if skill_gaps is None:
        return []

    if hasattr(skill_gaps, "to_dict"):

        try:
            skill_gaps = skill_gaps.to_dict(
                orient="records"
            )
        except Exception:
            return []

    if not isinstance(skill_gaps, list):
        return []

    formatted = []

    for item in skill_gaps:

        if not isinstance(item, dict):
            continue

        skill = item.get(
            "skill",
            item.get(
                "missing_skill",
                ""
            )
        )

        if not skill:
            continue

        importance = item.get(
            "importance",
            item.get(
                "frequency",
                item.get(
                    "score",
                    0
                )
            )
        )

        formatted.append({
            "skill": str(skill).strip(),
            "importance": safe_float(importance)
        })

    return formatted


def format_learning_recommendations(
    recommendations: Any
) -> list:
    """Format learning recommendations."""

    if recommendations is None:
        return []

    if hasattr(recommendations, "to_dict"):

        try:
            recommendations = recommendations.to_dict(
                orient="records"
            )
        except Exception:
            return []

    if not isinstance(recommendations, list):
        return []

    formatted = []

    for item in recommendations:

        if not isinstance(item, dict):
            continue

        skill = item.get(
            "skill",
            item.get(
                "missing_skill",
                ""
            )
        )

        if not skill:
            continue

        formatted.append({
            "skill": str(skill).strip(),

            "reason": item.get(
                "reason",
                "This skill can improve your job match."
            )
        })

    return formatted


def build_clean_response(
    analysis_result: dict
) -> dict:
    """
    Convert the internal analysis result into
    a frontend-friendly API response.
    """

    if not isinstance(analysis_result, dict):
        analysis_result = {}

    # -------------------------------------------------
    # Candidate
    # -------------------------------------------------

    candidate_data = analysis_result.get(
        "candidate",
        {}
    )

    if not isinstance(candidate_data, dict):
        candidate_data = {}

    candidate = {
        "name": candidate_data.get(
            "name",
            "Candidate"
        ),

        "candidate_id": candidate_data.get(
            "candidate_id",
            analysis_result.get(
                "candidate_id",
                ""
            )
        ),

        "education": candidate_data.get(
            "education",
            ""
        ),

        "experience": safe_float(
            candidate_data.get(
                "experience",
                candidate_data.get(
                    "experience_years",
                    0
                )
            )
        )
    }

    # -------------------------------------------------
    # Overall score
    # -------------------------------------------------

    overall_score = safe_float(
        analysis_result.get(
            "overall_score",
            analysis_result.get(
                "match_percentage",
                analysis_result.get(
                    "final_match_score",
                    0
                )
            )
        )
    )

    classification = analysis_result.get(
        "classification",
        analysis_result.get(
            "match_classification",
            ""
        )
    )

    # -------------------------------------------------
    # Skills
    # -------------------------------------------------

    skills_data = analysis_result.get(
        "skills",
        {}
    )

    if not isinstance(skills_data, dict):
        skills_data = {}

    matched_skills = clean_skill_list(
        skills_data.get(
            "matched",
            analysis_result.get(
                "matched_skills",
                []
            )
        )
    )

    missing_skills = clean_skill_list(
        skills_data.get(
            "missing",
            analysis_result.get(
                "missing_skills",
                []
            )
        )
    )

    # -------------------------------------------------
    # Recommendations
    # -------------------------------------------------

    job_recommendations = format_job_recommendations(
        analysis_result.get(
            "job_recommendations",
            analysis_result.get(
                "recommendations",
                []
            )
        )
    )

    # -------------------------------------------------
    # Skill gaps
    # -------------------------------------------------

    skill_gaps = format_skill_gaps(
        analysis_result.get(
            "skill_gaps",
            []
        )
    )

    # -------------------------------------------------
    # Learning recommendations
    # -------------------------------------------------

    learning_recommendations = (
        format_learning_recommendations(
            analysis_result.get(
                "learning_recommendations",
                analysis_result.get(
                    "learning",
                    []
                )
            )
        )
    )

    # -------------------------------------------------
    # Final response
    # -------------------------------------------------

    return {
        "candidate": candidate,

        "overall_score": overall_score,

        "classification": classification,

        "skills": {
            "matched": matched_skills,
            "missing": missing_skills
        },

        "job_recommendations": job_recommendations,

        "skill_gaps": skill_gaps,

        "learning_recommendations": (
            learning_recommendations
        )
    }