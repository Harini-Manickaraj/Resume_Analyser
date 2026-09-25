from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# AI BASED RESUME INTELLIGENCE AND JOB RECOMMENDATION SYSTEM
# LIGHTWEIGHT SEMANTIC SIMILARITY MODULE
# ============================================================


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DATA_DIR = PROJECT_ROOT / "data" / "datasets"

OUTPUT_DIR = DATA_DIR / "processed"

RESUME_FILE = DATA_DIR / "resume_profiles.csv"

JOB_FILE = DATA_DIR / "job_descriptions.csv"

OUTPUT_FILE = OUTPUT_DIR / "semantic_similarity_results.csv"


# ------------------------------------------------------------
# Build resume text
# ------------------------------------------------------------

def build_resume_text(row):

    sections = [
        str(row.get("summary", "")),
        str(row.get("skills", "")),
        str(row.get("education", "")),
        str(row.get("project_skills", "")),
        str(row.get("certifications", "")),
        str(row.get("soft_skills", ""))
    ]

    return " ".join(sections).strip()


# ------------------------------------------------------------
# Build job description text
# ------------------------------------------------------------

def build_job_text(row):

    sections = [
        str(row.get("job_title", "")),
        str(row.get("domain", "")),
        str(row.get("required_skills", "")),
        str(row.get("education_required", "")),
        str(row.get("responsibilities", ""))
    ]

    return " ".join(sections).strip()


# ------------------------------------------------------------
# Generate semantic matches
# ------------------------------------------------------------

def generate_semantic_matches(resume_df, job_df):

    print("\nPreparing resume text...")

    resume_texts = [
        build_resume_text(row)
        for _, row in resume_df.iterrows()
    ]

    print(f"✓ Prepared {len(resume_texts)} resume(s)")

    print("\nPreparing job description text...")

    job_texts = [
        build_job_text(row)
        for _, row in job_df.iterrows()
    ]

    print(f"✓ Prepared {len(job_texts)} job descriptions")

    # --------------------------------------------------------
    # Combine texts for one shared TF-IDF vocabulary
    # --------------------------------------------------------

    all_texts = resume_texts + job_texts

    print("\nGenerating TF-IDF vectors...")

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=5000
    )

    tfidf_matrix = vectorizer.fit_transform(all_texts)

    resume_vectors = tfidf_matrix[:len(resume_texts)]

    job_vectors = tfidf_matrix[len(resume_texts):]

    print("✓ TF-IDF vectors generated")

    # --------------------------------------------------------
    # Calculate similarity matrix
    # --------------------------------------------------------

    print("\nCalculating semantic similarities...")

    similarity_matrix = cosine_similarity(
        resume_vectors,
        job_vectors
    )

    results = []

    for resume_index, resume_row in resume_df.iterrows():

        for job_index, job_row in job_df.iterrows():

            similarity = (
                similarity_matrix[resume_index][job_index] * 100
            )

            results.append({

                "candidate_id":
                    resume_row["candidate_id"],

                "job_id":
                    job_row["job_id"],

                "job_title":
                    job_row["job_title"],

                "semantic_similarity":
                    round(float(similarity), 2)
            })

    return pd.DataFrame(results)


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

if __name__ == "__main__":

    print("=" * 70)
    print("AI RESUME INTELLIGENCE SYSTEM")
    print("TF-IDF SEMANTIC SIMILARITY ENGINE")
    print("=" * 70)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if not RESUME_FILE.exists():

        raise FileNotFoundError(
            f"Resume dataset not found:\n{RESUME_FILE}"
        )

    if not JOB_FILE.exists():

        raise FileNotFoundError(
            f"Job dataset not found:\n{JOB_FILE}"
        )

    print("\nLoading datasets...")

    resume_df = pd.read_csv(
        RESUME_FILE
    )

    job_df = pd.read_csv(
        JOB_FILE
    )

    print(f"✓ Resumes: {len(resume_df)}")
    print(f"✓ Jobs: {len(job_df)}")

    results = generate_semantic_matches(
        resume_df,
        job_df
    )

    results.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"\n✓ Results saved to:\n{OUTPUT_FILE}"
    )

    print("\n" + "=" * 70)
    print("TOP SEMANTIC JOB MATCHES")
    print("=" * 70)

    top_results = results.sort_values(
        by="semantic_similarity",
        ascending=False
    )

    print(
        top_results[
            [
                "candidate_id",
                "job_id",
                "job_title",
                "semantic_similarity"
            ]
        ].head(10).to_string(index=False)
    )

    print("\n" + "=" * 70)
    print("SEMANTIC SIMILARITY COMPLETED")
    print("=" * 70)