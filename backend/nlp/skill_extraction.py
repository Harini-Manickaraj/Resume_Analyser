import pandas as pd
import re
from pathlib import Path


# ============================================================
# AI BASED RESUME INTELLIGENCE AND JOB RECOMMENDATION SYSTEM
# SKILL EXTRACTION AND NORMALIZATION
# ============================================================


# ------------------------------------------------------------
# Project paths
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DATA_DIR = PROJECT_ROOT / "data" / "datasets"

SKILL_FILE = DATA_DIR / "skill_dictionary.csv"


# ------------------------------------------------------------
# Load skill dictionary
# ------------------------------------------------------------

def load_skill_dictionary(path=None):
    """
    Load the skill dictionary CSV.

    Parameters
    ----------
    path : str or Path, optional
        Explicit path to the CSV file.
        Defaults to the module-level SKILL_FILE constant.
    """

    target = Path(path) if path else SKILL_FILE

    if not target.exists():
        raise FileNotFoundError(
            f"Skill dictionary not found:\n{target}"
        )

    skill_df = pd.read_csv(target)

    return skill_df


# ------------------------------------------------------------
# Prepare aliases
# ------------------------------------------------------------

def prepare_skill_dictionary(skill_df):

    skill_mapping = {}

    for _, row in skill_df.iterrows():

        canonical_skill = str(
            row["canonical_skill"]
        ).strip()

        if not canonical_skill:
            continue

        # Add canonical skill itself
        skill_mapping[
            canonical_skill.lower()
        ] = canonical_skill

        # Add aliases
        aliases_value = row.get(
            "aliases",
            ""
        )

        if pd.isna(aliases_value):
            aliases_value = ""

        aliases = str(
            aliases_value
        ).split(";")

        for alias in aliases:

            alias = alias.strip()

            if alias:

                skill_mapping[
                    alias.lower()
                ] = canonical_skill

    return skill_mapping


# ------------------------------------------------------------
# Normalize a single skill
# ------------------------------------------------------------

def normalize_skill(skill, skill_mapping):

    if not isinstance(skill, str):
        return ""

    skill = skill.strip().lower()

    if not skill:
        return ""

    return skill_mapping.get(
        skill,
        ""
    )


# ------------------------------------------------------------
# Extract skills from free text
# ------------------------------------------------------------

def extract_skills(text, skill_mapping):

    if not isinstance(text, str):

        return []

    text_lower = text.lower()

    extracted_skills = set()

    # Sort longest aliases first
    sorted_aliases = sorted(
        skill_mapping.keys(),
        key=len,
        reverse=True
    )

    for alias in sorted_aliases:

        escaped_alias = re.escape(
            alias
        )

        pattern = (
            r"(?<!\w)"
            + escaped_alias
            + r"(?!\w)"
        )

        if re.search(
            pattern,
            text_lower
        ):

            canonical_skill = (
                skill_mapping[alias]
            )

            extracted_skills.add(
                canonical_skill
            )

    return sorted(
        extracted_skills
    )


# ------------------------------------------------------------
# Extract skills from structured list/string
# ------------------------------------------------------------

def extract_skills_from_list(
    skills,
    skill_mapping
):

    normalized_skills = set()

    # --------------------------------------------------------
    # IMPORTANT FIX
    #
    # The dataset may contain:
    #
    # Python, SQL, Pandas
    #
    # or:
    #
    # Python;SQL;Pandas
    #
    # or an actual Python list.
    # --------------------------------------------------------

    if skills is None:
        return []

    if isinstance(skills, float) and pd.isna(skills):
        return []

    # --------------------------------------------------------
    # If input is a string
    # --------------------------------------------------------

    if isinstance(skills, str):

        skills_text = skills.strip()

        if not skills_text:
            return []

        # Remove list brackets if present
        if (
            skills_text.startswith("[")
            and skills_text.endswith("]")
        ):

            skills_text = skills_text[
                1:-1
            ]

        # Support both comma and semicolon
        # separators
        individual_skills = re.split(
            r"[;,]",
            skills_text
        )

    # --------------------------------------------------------
    # If input is already a list
    # --------------------------------------------------------

    elif isinstance(skills, (list, tuple, set)):

        individual_skills = []

        for item in skills:

            if not isinstance(
                item,
                str
            ):
                continue

            # A list item itself may contain
            # comma/semicolon separated values
            individual_skills.extend(
                re.split(
                    r"[;,]",
                    item
                )
            )

    else:

        return []

    # --------------------------------------------------------
    # Normalize each skill
    # --------------------------------------------------------

    for individual_skill in individual_skills:

        individual_skill = (
            individual_skill
            .strip()
            .strip("'")
            .strip('"')
        )

        if not individual_skill:
            continue

        normalized = normalize_skill(
            individual_skill,
            skill_mapping
        )

        # IMPORTANT:
        # Only keep skills that exist in the
        # skill dictionary.
        if normalized:

            normalized_skills.add(
                normalized
            )

    return sorted(
        normalized_skills
    )


# ------------------------------------------------------------
# Compare resume skills with job skills
# ------------------------------------------------------------

def compare_skills(
    resume_skills,
    job_skills
):

    # Normalize both sides
    resume_set = {
        skill
        for skill in resume_skills
        if isinstance(skill, str)
        and skill.strip()
    }

    job_set = {
        skill
        for skill in job_skills
        if isinstance(skill, str)
        and skill.strip()
    }

    matched_skills = sorted(
        resume_set.intersection(
            job_set
        )
    )

    missing_skills = sorted(
        job_set.difference(
            resume_set
        )
    )

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_count": len(
            matched_skills
        ),
        "required_skill_count": len(
            job_set
        )
    }


# ------------------------------------------------------------
# Test the module
# ------------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print(
        "SKILL EXTRACTION AND NORMALIZATION"
    )
    print("=" * 60)

    # --------------------------------------------------------
    # Load dictionary
    # --------------------------------------------------------

    skill_df = load_skill_dictionary()

    print(
        f"\nSkill dictionary loaded: "
        f"{len(skill_df)} entries"
    )

    # --------------------------------------------------------
    # Prepare mapping
    # --------------------------------------------------------

    skill_mapping = (
        prepare_skill_dictionary(
            skill_df
        )
    )

    print(
        f"Skill aliases loaded: "
        f"{len(skill_mapping)}"
    )

    # --------------------------------------------------------
    # Test free text extraction
    # --------------------------------------------------------

    sample_text = """
    I have experience in Python, Pandas, NumPy,
    Machine Learning, SQL and Scikit-learn.
    I have also worked with ML models using XGBoost
    and Django for web application development.
    """

    extracted_skills = extract_skills(
        sample_text,
        skill_mapping
    )

    print("\n" + "-" * 60)
    print("SAMPLE TEXT")
    print("-" * 60)

    print(sample_text)

    print("\n" + "-" * 60)
    print("EXTRACTED SKILLS")
    print("-" * 60)

    for skill in extracted_skills:

        print(f"✓ {skill}")

    # --------------------------------------------------------
    # Test structured skill extraction
    # --------------------------------------------------------

    test_skill_string = (
        "Python, SQL, Pandas, NumPy, Excel"
    )

    normalized = extract_skills_from_list(
        test_skill_string,
        skill_mapping
    )

    print("\n" + "-" * 60)
    print("STRUCTURED SKILL TEST")
    print("-" * 60)

    print(
        "Input:",
        test_skill_string
    )

    print(
        "Output:",
        normalized
    )

    # --------------------------------------------------------
    # Test normalization
    # --------------------------------------------------------

    test_skills = [
        "python",
        "ML",
        "sklearn",
        "Pandas",
        "numpy",
        "XGBoost"
    ]

    print("\n" + "-" * 60)
    print("NORMALIZATION TEST")
    print("-" * 60)

    for skill in test_skills:

        print(
            f"{skill:15} → "
            f"{normalize_skill(skill, skill_mapping)}"
        )

    # --------------------------------------------------------
    # Test comparison
    # --------------------------------------------------------

    resume_skills = [
        "Python",
        "Pandas",
        "NumPy",
        "SQL",
        "Scikit-learn"
    ]

    job_skills = [
        "Python",
        "Pandas",
        "NumPy",
        "SQL",
        "Machine Learning",
        "Docker"
    ]

    comparison = compare_skills(
        resume_skills,
        job_skills
    )

    print("\n" + "-" * 60)
    print("SKILL COMPARISON")
    print("-" * 60)

    print(
        "Matched Skills:",
        comparison[
            "matched_skills"
        ]
    )

    print(
        "Missing Skills:",
        comparison[
            "missing_skills"
        ]
    )

    print(
        "Match Count:",
        comparison[
            "match_count"
        ]
    )

    print(
        "Required Skills:",
        comparison[
            "required_skill_count"
        ]
    )

    print("\n" + "=" * 60)
    print(
        "SKILL MODULE TEST COMPLETED"
    )
    print("=" * 60)