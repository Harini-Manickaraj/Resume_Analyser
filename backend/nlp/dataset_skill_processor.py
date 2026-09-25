import sys
from pathlib import Path

import pandas as pd


# ------------------------------------------------------------
# Allow Python to find the backend package
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

sys.path.insert(
    0,
    str(PROJECT_ROOT)
)


from backend.nlp.skill_extraction import (
    load_skill_dictionary,
    prepare_skill_dictionary,
    extract_skills,
    extract_skills_from_list,
    compare_skills
)


# ============================================================
# AI BASED RESUME INTELLIGENCE AND JOB RECOMMENDATION SYSTEM
# DATASET SKILL PROCESSOR
# ============================================================


# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------

DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "datasets"
)

RESUME_FILE = (
    DATA_DIR
    / "resume_profiles.csv"
)

JOB_FILE = (
    DATA_DIR
    / "job_descriptions.csv"
)

OUTPUT_DIR = (
    DATA_DIR
    / "processed"
)

OUTPUT_RESUME_FILE = (
    OUTPUT_DIR
    / "processed_resume_skills.csv"
)

OUTPUT_JOB_FILE = (
    OUTPUT_DIR
    / "processed_job_skills.csv"
)

OUTPUT_MATCH_FILE = (
    OUTPUT_DIR
    / "skill_match_results.csv"
)


# ------------------------------------------------------------
# Load datasets
# ------------------------------------------------------------

def load_datasets():

    print("\nLoading datasets...")

    if not RESUME_FILE.exists():

        raise FileNotFoundError(
            f"Resume dataset not found:\n"
            f"{RESUME_FILE}"
        )

    if not JOB_FILE.exists():

        raise FileNotFoundError(
            f"Job dataset not found:\n"
            f"{JOB_FILE}"
        )

    resume_df = pd.read_csv(
        RESUME_FILE
    )

    job_df = pd.read_csv(
        JOB_FILE
    )

    print(
        f"✓ Resumes loaded: "
        f"{len(resume_df)}"
    )

    print(
        f"✓ Job descriptions loaded: "
        f"{len(job_df)}"
    )

    return (
        resume_df,
        job_df
    )


# ------------------------------------------------------------
# Process resume skills
# ------------------------------------------------------------

def process_resumes(
    resume_df,
    skill_mapping
):

    processed_resumes = []

    for _, row in resume_df.iterrows():

        candidate_id = row[
            "candidate_id"
        ]

        # ----------------------------------------------------
        # Structured resume skills
        # ----------------------------------------------------

        resume_skills = (
            extract_skills_from_list(
                row.get(
                    "skills",
                    ""
                ),
                skill_mapping
            )
        )

        # ----------------------------------------------------
        # Summary skills
        # ----------------------------------------------------

        summary_skills = extract_skills(
            row.get(
                "summary",
                ""
            ),
            skill_mapping
        )

        # ----------------------------------------------------
        # Project skills
        # ----------------------------------------------------

        project_skills = extract_skills(
            row.get(
                "project_skills",
                ""
            ),
            skill_mapping
        )

        # ----------------------------------------------------
        # Combine all skills
        # ----------------------------------------------------

        all_skills = sorted(
            set(
                resume_skills
                + summary_skills
                + project_skills
            )
        )

        processed_resumes.append({

            "candidate_id":
                candidate_id,

            "normalized_skills":
                ";".join(
                    all_skills
                ),

            "skill_count":
                len(all_skills)
        })

    return pd.DataFrame(
        processed_resumes
    )


# ------------------------------------------------------------
# Process job descriptions
# ------------------------------------------------------------

def process_jobs(
    job_df,
    skill_mapping
):

    processed_jobs = []

    for _, row in job_df.iterrows():

        job_id = row[
            "job_id"
        ]

        # ----------------------------------------------------
        # Required skills
        # ----------------------------------------------------

        required_skills = (
            extract_skills_from_list(
                row.get(
                    "required_skills",
                    ""
                ),
                skill_mapping
            )
        )

        # ----------------------------------------------------
        # Skills mentioned in responsibilities
        # ----------------------------------------------------

        responsibility_skills = extract_skills(
            row.get(
                "responsibilities",
                ""
            ),
            skill_mapping
        )

        # ----------------------------------------------------
        # Combine skills
        # ----------------------------------------------------

        all_skills = sorted(
            set(
                required_skills
                + responsibility_skills
            )
        )

        processed_jobs.append({

            "job_id":
                job_id,

            "job_title":
                row[
                    "job_title"
                ],

            "normalized_required_skills":
                ";".join(
                    all_skills
                ),

            "skill_count":
                len(all_skills)
        })

    return pd.DataFrame(
        processed_jobs
    )


# ------------------------------------------------------------
# Calculate skill matching
# ------------------------------------------------------------

def calculate_skill_matches(
    resume_df,
    job_df
):

    results = []

    for _, resume in resume_df.iterrows():

        # ----------------------------------------------------
        # Candidate skills
        # ----------------------------------------------------

        resume_skills = set(
            filter(
                None,
                str(
                    resume[
                        "normalized_skills"
                    ]
                ).split(";")
            )
        )

        for _, job in job_df.iterrows():

            # ------------------------------------------------
            # Job skills
            # ------------------------------------------------

            job_skills = set(
                filter(
                    None,
                    str(
                        job[
                            "normalized_required_skills"
                        ]
                    ).split(";")
                )
            )

            # ------------------------------------------------
            # Compare
            # ------------------------------------------------

            comparison = compare_skills(
                resume_skills,
                job_skills
            )

            required_count = (
                comparison[
                    "required_skill_count"
                ]
            )

            matched_count = (
                comparison[
                    "match_count"
                ]
            )

            # ------------------------------------------------
            # Percentage
            # ------------------------------------------------

            if required_count > 0:

                skill_match_percentage = (
                    matched_count
                    / required_count
                ) * 100

            else:

                skill_match_percentage = 0.0

            # ------------------------------------------------
            # Save result
            # ------------------------------------------------

            results.append({

                "candidate_id":
                    resume[
                        "candidate_id"
                    ],

                "job_id":
                    job[
                        "job_id"
                    ],

                "job_title":
                    job[
                        "job_title"
                    ],

                "matched_skills":
                    ";".join(
                        comparison[
                            "matched_skills"
                        ]
                    ),

                "missing_skills":
                    ";".join(
                        comparison[
                            "missing_skills"
                        ]
                    ),

                "matched_skill_count":
                    matched_count,

                "required_skill_count":
                    required_count,

                "skill_match_percentage":
                    round(
                        skill_match_percentage,
                        2
                    )
            })

    return pd.DataFrame(
        results
    )


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print(
        "AI RESUME INTELLIGENCE SYSTEM"
    )
    print(
        "DATASET SKILL PROCESSING"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # Create output directory
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Load skill dictionary
    # --------------------------------------------------------

    print(
        "\nLoading skill dictionary..."
    )

    skill_df = load_skill_dictionary()

    skill_mapping = (
        prepare_skill_dictionary(
            skill_df
        )
    )

    print(
        f"✓ {len(skill_mapping)} "
        f"skill aliases loaded"
    )

    # --------------------------------------------------------
    # Load datasets
    # --------------------------------------------------------

    resume_df, job_df = (
        load_datasets()
    )

    # --------------------------------------------------------
    # Process resumes
    # --------------------------------------------------------

    print(
        "\nProcessing resume skills..."
    )

    processed_resumes = (
        process_resumes(
            resume_df,
            skill_mapping
        )
    )

    processed_resumes.to_csv(
        OUTPUT_RESUME_FILE,
        index=False
    )

    print(
        f"✓ Resume skills saved to:\n"
        f"  {OUTPUT_RESUME_FILE}"
    )

    # --------------------------------------------------------
    # Process jobs
    # --------------------------------------------------------

    print(
        "\nProcessing job description skills..."
    )

    processed_jobs = (
        process_jobs(
            job_df,
            skill_mapping
        )
    )

    processed_jobs.to_csv(
        OUTPUT_JOB_FILE,
        index=False
    )

    print(
        f"✓ Job skills saved to:\n"
        f"  {OUTPUT_JOB_FILE}"
    )

    # --------------------------------------------------------
    # Calculate matching
    # --------------------------------------------------------

    print(
        "\nCalculating skill matches..."
    )

    match_results = (
        calculate_skill_matches(
            processed_resumes,
            processed_jobs
        )
    )

    match_results.to_csv(
        OUTPUT_MATCH_FILE,
        index=False
    )

    print(
        f"✓ Matching results saved to:\n"
        f"  {OUTPUT_MATCH_FILE}"
    )

    # --------------------------------------------------------
    # Display top matches
    # --------------------------------------------------------

    print(
        "\n"
        + "=" * 70
    )

    print(
        "TOP JOB MATCHES"
    )

    print(
        "=" * 70
    )

    top_matches = (
        match_results
        .sort_values(
            by="skill_match_percentage",
            ascending=False
        )
    )

    print(
        top_matches[
            [
                "candidate_id",
                "job_id",
                "job_title",
                "matched_skills",
                "missing_skills",
                "skill_match_percentage"
            ]
        ]
        .head(10)
        .to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print(
        "\n"
        + "=" * 70
    )

    print(
        "PROCESSING COMPLETED"
    )

    print(
        "=" * 70
    )

    print(
        f"\nResume records processed : "
        f"{len(processed_resumes)}"
    )

    print(
        f"Job records processed    : "
        f"{len(processed_jobs)}"
    )

    print(
        f"Match records generated  : "
        f"{len(match_results)}"
    )

    print(
        "\nGenerated files:"
    )

    print(
        f"1. {OUTPUT_RESUME_FILE}"
    )

    print(
        f"2. {OUTPUT_JOB_FILE}"
    )

    print(
        f"3. {OUTPUT_MATCH_FILE}"
    )