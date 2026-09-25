import pandas as pd
from pathlib import Path


# ============================================================
# AI BASED RESUME INTELLIGENCE AND JOB RECOMMENDATION SYSTEM
# Dataset Loader
# ============================================================

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Dataset directory
DATA_DIR = PROJECT_ROOT / "data" / "datasets"


# ------------------------------------------------------------
# Load datasets
# ------------------------------------------------------------

def load_datasets():

    resume_file = DATA_DIR / "resume_profiles.csv"
    jobs_file = DATA_DIR / "job_descriptions.csv"
    labels_file = DATA_DIR / "initial_matching_labels.csv"
    skills_file = DATA_DIR / "skill_dictionary.csv"

    # Check whether files exist
    required_files = [
        resume_file,
        jobs_file,
        labels_file,
        skills_file
    ]

    for file in required_files:
        if not file.exists():
            raise FileNotFoundError(
                f"Dataset file not found:\n{file}"
            )

    # Read CSV files
    resume_df = pd.read_csv(resume_file)
    jobs_df = pd.read_csv(jobs_file)
    labels_df = pd.read_csv(labels_file)
    skills_df = pd.read_csv(skills_file)

    return resume_df, jobs_df, labels_df, skills_df


# ------------------------------------------------------------
# Main program
# ------------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("AI RESUME INTELLIGENCE SYSTEM")
    print("DATASET VALIDATION")
    print("=" * 60)

    try:

        # Load datasets
        resume_df, jobs_df, labels_df, skills_df = load_datasets()

        print("\n✓ All datasets loaded successfully!")

        # ----------------------------------------------------
        # Dataset information
        # ----------------------------------------------------

        print("\n" + "-" * 60)
        print("DATASET SHAPES")
        print("-" * 60)

        print(f"Resume Profiles       : {resume_df.shape}")
        print(f"Job Descriptions      : {jobs_df.shape}")
        print(f"Matching Labels       : {labels_df.shape}")
        print(f"Skill Dictionary      : {skills_df.shape}")

        # ----------------------------------------------------
        # Column information
        # ----------------------------------------------------

        print("\n" + "-" * 60)
        print("COLUMNS")
        print("-" * 60)

        print("\nResume Profiles:")
        print(resume_df.columns.tolist())

        print("\nJob Descriptions:")
        print(jobs_df.columns.tolist())

        print("\nMatching Labels:")
        print(labels_df.columns.tolist())

        print("\nSkill Dictionary:")
        print(skills_df.columns.tolist())

        # ----------------------------------------------------
        # Missing values
        # ----------------------------------------------------

        print("\n" + "-" * 60)
        print("MISSING VALUES")
        print("-" * 60)

        print("\nResume Profiles:")
        print(resume_df.isnull().sum())

        print("\nJob Descriptions:")
        print(jobs_df.isnull().sum())

        print("\nMatching Labels:")
        print(labels_df.isnull().sum())

        print("\nSkill Dictionary:")
        print(skills_df.isnull().sum())

        # ----------------------------------------------------
        # Preview data
        # ----------------------------------------------------

        print("\n" + "-" * 60)
        print("RESUME DATA")
        print("-" * 60)

        print(resume_df.head())

        print("\n" + "-" * 60)
        print("JOB DESCRIPTION DATA")
        print("-" * 60)

        print(jobs_df.head())

        print("\n" + "-" * 60)
        print("MATCHING LABEL DATA")
        print("-" * 60)

        print(labels_df.head())

        print("\n" + "-" * 60)
        print("SKILL DICTIONARY")
        print("-" * 60)

        print(skills_df.head())

        # ----------------------------------------------------
        # Basic validation
        # ----------------------------------------------------

        print("\n" + "=" * 60)
        print("DATASET VALIDATION COMPLETED")
        print("=" * 60)

    except Exception as e:

        print("\n✗ ERROR")
        print(e)