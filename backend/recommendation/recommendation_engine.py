from pathlib import Path
from collections import Counter
import ast
import pandas as pd


# ============================================================
# PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DATA_DIR = PROJECT_ROOT / "data" / "datasets"
PROCESSED_DIR = DATA_DIR / "processed"

HYBRID_FILE = (
    PROCESSED_DIR / "hybrid_matching_results.csv"
)

JOB_FILE = (
    DATA_DIR / "job_descriptions.csv"
)

SKILL_DICTIONARY_FILE = (
    DATA_DIR / "skill_dictionary.csv"
)

OUTPUT_RECOMMENDATIONS = (
    PROCESSED_DIR / "job_recommendations.csv"
)

OUTPUT_SKILL_GAPS = (
    PROCESSED_DIR / "skill_gap_analysis.csv"
)

OUTPUT_LEARNING = (
    PROCESSED_DIR / "learning_recommendations.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

TOP_N_JOBS = 5


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def safe_string(value):
    """
    Convert any value to a safe string.
    """

    if pd.isna(value):
        return ""

    return str(value).strip()


def normalize_skill(skill):
    """
    Normalize a skill for comparison.
    """

    return (
        safe_string(skill)
        .lower()
        .replace("-", " ")
        .replace("_", " ")
    )


def parse_skill_list(value):
    """
    Convert different skill formats into a Python list.

    Supported formats:

    Python list:
        ['Python', 'SQL']

    Semicolon separated:
        Python;SQL;Pandas

    Comma separated:
        Python, SQL, Pandas
    """

    if pd.isna(value):
        return []

    text = str(value).strip()

    if not text:
        return []

    # Python list format
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

    # Semicolon separated
    if ";" in text:

        return [
            item.strip()
            for item in text.split(";")
            if item.strip()
        ]

    # Comma separated
    if "," in text:

        return [
            item.strip()
            for item in text.split(",")
            if item.strip()
        ]

    return [text]


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    print("=" * 60)
    print("LOADING RECOMMENDATION DATA")
    print("=" * 60)

    if not HYBRID_FILE.exists():

        raise FileNotFoundError(
            f"Hybrid matching file not found:\n"
            f"{HYBRID_FILE}"
        )

    if not JOB_FILE.exists():

        raise FileNotFoundError(
            f"Job description file not found:\n"
            f"{JOB_FILE}"
        )

    hybrid_results = pd.read_csv(
        HYBRID_FILE
    )

    jobs = pd.read_csv(
        JOB_FILE
    )

    # Skill dictionary is optional
    if SKILL_DICTIONARY_FILE.exists():

        skill_dictionary = pd.read_csv(
            SKILL_DICTIONARY_FILE
        )

    else:

        skill_dictionary = pd.DataFrame()

    print(
        f"Hybrid matching records: "
        f"{len(hybrid_results)}"
    )

    print(
        f"Job descriptions: {len(jobs)}"
    )

    print(
        f"Skill dictionary records: "
        f"{len(skill_dictionary)}"
    )

    return (
        hybrid_results,
        jobs,
        skill_dictionary
    )


# ============================================================
# SKILL DICTIONARY
# ============================================================

def build_skill_categories(skill_dictionary):

    """
    Build:

        skill -> category

    mapping from the skill dictionary.
    """

    category_map = {}

    if skill_dictionary.empty:

        return category_map

    for _, row in skill_dictionary.iterrows():

        skill = safe_string(
            row.get("canonical_skill", "")
        )

        category = safe_string(
            row.get("category", "Other")
        )

        if skill:

            category_map[
                normalize_skill(skill)
            ] = category

    return category_map


# ============================================================
# JOB RANKING
# ============================================================

def rank_jobs(hybrid_results):

    """
    Rank jobs according to final hybrid score.
    """

    ranked = hybrid_results.copy()

    ranked["final_match_score"] = pd.to_numeric(
        ranked["final_match_score"],
        errors="coerce"
    ).fillna(0)

    ranked["match_percentage"] = pd.to_numeric(
        ranked["match_percentage"],
        errors="coerce"
    ).fillna(
        ranked["final_match_score"] * 100
    )

    ranked = ranked.sort_values(
        by="final_match_score",
        ascending=False
    ).reset_index(drop=True)

    return ranked


# ============================================================
# TOP JOB RECOMMENDATIONS
# ============================================================

def generate_job_recommendations(
    hybrid_results,
    jobs
):

    """
    Generate top N job recommendations.
    """

    ranked = rank_jobs(
        hybrid_results
    )

    top_jobs = ranked.head(
        TOP_N_JOBS
    ).copy()

    # Add ranking
    top_jobs.insert(
        0,
        "recommendation_rank",
        range(
            1,
            len(top_jobs) + 1
        )
    )

    # Add job domain
    if "job_id" in top_jobs.columns:

        top_jobs = top_jobs.merge(
            jobs[
                [
                    "job_id",
                    "domain",
                    "required_skills",
                    "responsibilities"
                ]
            ],
            on="job_id",
            how="left",
            suffixes=("", "_job")
        )

    # Recommendation reason
    reasons = []

    for _, row in top_jobs.iterrows():

        score = float(
            row.get(
                "match_percentage",
                0
            )
        )

        classification = safe_string(
            row.get(
                "match_classification",
                ""
            )
        )

        matched = parse_skill_list(
            row.get(
                "matched_skills",
                ""
            )
        )

        missing = parse_skill_list(
            row.get(
                "missing_skills",
                ""
            )
        )

        reason = (
            f"{classification} with "
            f"{score:.2f}% overall compatibility. "
        )

        if matched:

            reason += (
                f"Strong overlap in "
                f"{', '.join(matched[:4])}. "
            )

        if missing:

            reason += (
                f"Consider improving "
                f"{', '.join(missing[:3])}."
            )

        reasons.append(reason)

    top_jobs[
        "recommendation_reason"
    ] = reasons

    return top_jobs


# ============================================================
# SKILL GAP ANALYSIS
# ============================================================

def generate_skill_gap_analysis(
    hybrid_results,
    skill_category_map
):

    """
    Analyze missing skills across all jobs.

    A skill receives a higher priority when:

    1. It is required by many jobs.
    2. It is missing from the candidate.
    3. It appears in higher-ranked jobs.
    """

    skill_frequency = Counter()

    skill_weight = Counter()

    skill_job_map = {}

    # --------------------------------------------------------
    # Analyze every job
    # --------------------------------------------------------

    for _, row in hybrid_results.iterrows():

        score = float(
            row.get(
                "final_match_score",
                0
            )
        )

        job_id = safe_string(
            row.get(
                "job_id",
                ""
            )
        )

        missing_skills = parse_skill_list(
            row.get(
                "missing_skills",
                ""
            )
        )

        for skill in missing_skills:

            normalized = normalize_skill(
                skill
            )

            if not normalized:
                continue

            skill_frequency[
                normalized
            ] += 1

            # Higher score = more relevant
            # to candidate
            skill_weight[
                normalized
            ] += score

            if normalized not in skill_job_map:

                skill_job_map[
                    normalized
                ] = []

            if job_id:

                skill_job_map[
                    normalized
                ].append(job_id)

    # --------------------------------------------------------
    # Create records
    # --------------------------------------------------------

    gap_records = []

    for skill in skill_frequency:

        frequency = skill_frequency[
            skill
        ]

        relevance = skill_weight[
            skill
        ]

        # Priority score
        priority_score = (
            frequency * 0.5
            + relevance * 0.5
        )

        category = skill_category_map.get(
            skill,
            "Other"
        )

        gap_records.append({

            "skill": skill.title(),

            "category": category,

            "job_frequency": frequency,

            "job_relevance_score": round(
                relevance,
                4
            ),

            "skill_gap_priority": round(
                priority_score,
                4
            ),

            "related_jobs": ";".join(
                skill_job_map[
                    skill
                ]
            )
        })

    gap_df = pd.DataFrame(
        gap_records
    )

    if not gap_df.empty:

        gap_df = gap_df.sort_values(
            by="skill_gap_priority",
            ascending=False
        ).reset_index(
            drop=True
        )

        gap_df.insert(
            0,
            "priority_rank",
            range(
                1,
                len(gap_df) + 1
            )
        )

    return gap_df


# ============================================================
# LEARNING RECOMMENDATIONS
# ============================================================

def generate_learning_recommendations(
    skill_gap_df
):

    """
    Convert skill gaps into recommended
    learning areas.
    """

    learning_records = []

    for _, row in skill_gap_df.iterrows():

        skill = safe_string(
            row.get(
                "skill",
                ""
            )
        )

        category = safe_string(
            row.get(
                "category",
                "Other"
            )
        )

        priority = float(
            row.get(
                "skill_gap_priority",
                0
            )
        )

        frequency = int(
            row.get(
                "job_frequency",
                0
            )
        )

        # ----------------------------------------------------
        # Priority classification
        # ----------------------------------------------------

        if priority >= 2.5:

            priority_level = "High"

        elif priority >= 1.0:

            priority_level = "Medium"

        else:

            priority_level = "Low"

        # ----------------------------------------------------
        # Learning action
        # ----------------------------------------------------

        if category.lower() == "programming":

            action = (
                f"Build practical projects using "
                f"{skill} and practice implementation "
                f"through coding exercises."
            )

        elif category.lower() == "machine learning":

            action = (
                f"Study {skill} and implement "
                f"a machine learning project "
                f"using real-world data."
            )

        elif category.lower() == "data analysis":

            action = (
                f"Practice {skill} with "
                f"data cleaning, analysis, "
                f"visualization and reporting."
            )

        elif category.lower() == "database":

            action = (
                f"Practice {skill} by designing "
                f"databases and writing "
                f"real-world queries."
            )

        elif category.lower() == "cloud":

            action = (
                f"Learn {skill} fundamentals "
                f"and deploy a small data "
                f"or ML application."
            )

        elif category.lower() == "devops":

            action = (
                f"Practice {skill} by containerizing "
                f"and deploying an application."
            )

        else:

            action = (
                f"Learn {skill} through "
                f"documentation, tutorials "
                f"and a practical project."
            )

        learning_records.append({

            "skill": skill,

            "category": category,

            "priority": priority_level,

            "job_frequency": frequency,

            "skill_gap_priority": round(
                priority,
                4
            ),

            "recommended_action": action
        })

    return pd.DataFrame(
        learning_records
    )


# ============================================================
# CANDIDATE SUMMARY
# ============================================================

def generate_candidate_summary(
    recommendations,
    skill_gaps
):

    """
    Generate a console summary of the candidate.
    """

    print()
    print("=" * 60)
    print("CANDIDATE CAREER INTELLIGENCE SUMMARY")
    print("=" * 60)

    if recommendations.empty:

        print(
            "No job recommendations available."
        )

        return

    candidate_id = safe_string(
        recommendations.iloc[0].get(
            "candidate_id",
            ""
        )
    )

    print(
        f"Candidate: {candidate_id}"
    )

    print()
    print("TOP JOB RECOMMENDATIONS")
    print("-" * 60)

    for _, row in recommendations.iterrows():

        rank = row.get(
            "recommendation_rank",
            ""
        )

        title = row.get(
            "job_title",
            ""
        )

        score = row.get(
            "match_percentage",
            0
        )

        classification = row.get(
            "match_classification",
            ""
        )

        print(
            f"{rank}. {title}"
        )

        print(
            f"   Match: {score:.2f}%"
        )

        print(
            f"   Classification: "
            f"{classification}"
        )

        matched = parse_skill_list(
            row.get(
                "matched_skills",
                ""
            )
        )

        missing = parse_skill_list(
            row.get(
                "missing_skills",
                ""
            )
        )

        if matched:

            print(
                "   Matched: "
                + ", ".join(
                    matched[:5]
                )
            )

        if missing:

            print(
                "   Missing: "
                + ", ".join(
                    missing[:5]
                )
            )

        print()

    print(
        "=" * 60
    )

    print(
        "TOP SKILL GAPS"
    )

    print(
        "-" * 60
    )

    if skill_gaps.empty:

        print(
            "No significant skill gaps detected."
        )

    else:

        for _, row in skill_gaps.head(10).iterrows():

            print(
                f"{row['priority_rank']}. "
                f"{row['skill']} "
                f"({row['category']})"
            )

            print(
                f"   Priority: "
                f"{row['skill_gap_priority']:.2f}"
            )

            print(
                f"   Appears in "
                f"{row['job_frequency']} job(s)"
            )

            print()


# ============================================================
# MAIN ENGINE
# ============================================================

def run_recommendation_engine():

    print()
    print("=" * 60)
    print("AI JOB RECOMMENDATION ENGINE")
    print("=" * 60)

    # --------------------------------------------------------
    # Load datasets
    # --------------------------------------------------------

    (
        hybrid_results,
        jobs,
        skill_dictionary
    ) = load_data()

    # --------------------------------------------------------
    # Skill category mapping
    # --------------------------------------------------------

    skill_category_map = (
        build_skill_categories(
            skill_dictionary
        )
    )

    # --------------------------------------------------------
    # Generate job recommendations
    # --------------------------------------------------------

    recommendations = (
        generate_job_recommendations(
            hybrid_results,
            jobs
        )
    )

    # --------------------------------------------------------
    # Generate skill gap analysis
    # --------------------------------------------------------

    skill_gaps = (
        generate_skill_gap_analysis(
            hybrid_results,
            skill_category_map
        )
    )

    # --------------------------------------------------------
    # Generate learning recommendations
    # --------------------------------------------------------

    learning_recommendations = (
        generate_learning_recommendations(
            skill_gaps
        )
    )

    # --------------------------------------------------------
    # Create output directory
    # --------------------------------------------------------

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Save recommendations
    # --------------------------------------------------------

    recommendations.to_csv(
        OUTPUT_RECOMMENDATIONS,
        index=False
    )

    # --------------------------------------------------------
    # Save skill gaps
    # --------------------------------------------------------

    skill_gaps.to_csv(
        OUTPUT_SKILL_GAPS,
        index=False
    )

    # --------------------------------------------------------
    # Save learning recommendations
    # --------------------------------------------------------

    learning_recommendations.to_csv(
        OUTPUT_LEARNING,
        index=False
    )

    # --------------------------------------------------------
    # Display summary
    # --------------------------------------------------------

    generate_candidate_summary(
        recommendations,
        skill_gaps
    )

    # --------------------------------------------------------
    # Final output information
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("RECOMMENDATION ENGINE COMPLETED")
    print("=" * 60)

    print()
    print(
        "Generated files:"
    )

    print(
        f"1. {OUTPUT_RECOMMENDATIONS}"
    )

    print(
        f"2. {OUTPUT_SKILL_GAPS}"
    )

    print(
        f"3. {OUTPUT_LEARNING}"
    )

    print()
    print(
        f"Top jobs generated: "
        f"{len(recommendations)}"
    )

    print(
        f"Skill gaps detected: "
        f"{len(skill_gaps)}"
    )

    print(
        f"Learning recommendations: "
        f"{len(learning_recommendations)}"
    )

    return (
        recommendations,
        skill_gaps,
        learning_recommendations
    )


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":

    run_recommendation_engine()