import sys
from pathlib import Path

import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# AI BASED RESUME INTELLIGENCE AND JOB RECOMMENDATION SYSTEM
# SEMANTIC SIMILARITY MODULE
# ============================================================


# ------------------------------------------------------------
# Project paths
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DATA_DIR = PROJECT_ROOT / "data" / "datasets"

OUTPUT_DIR = DATA_DIR / "processed"

RESUME_FILE = DATA_DIR / "resume_profiles.csv"

JOB_FILE = DATA_DIR / "job_descriptions.csv"

OUTPUT_FILE = OUTPUT_DIR / "semantic_similarity_results.csv"


# ------------------------------------------------------------
# Sentence Transformer model
# ------------------------------------------------------------

MODEL_NAME = "all-MiniLM-L6-v2"


# ------------------------------------------------------------
# Load model
# ------------------------------------------------------------

def load_model():

    print("\nLoading Sentence Transformer model...")

    model = SentenceTransformer(MODEL_NAME)

    print(
        f"✓ Model loaded: {MODEL_NAME}"
    )

    return model


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

    text = " ".join(sections)

    return text.strip()


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

    text = " ".join(sections)

    return text.strip()


# ------------------------------------------------------------
# Calculate cosine similarity
# ------------------------------------------------------------

def calculate_similarity(
    resume_embedding,
    job_embedding
):

    similarity = cosine_similarity(
        [resume_embedding],
        [job_embedding]
    )[0][0]

    # Convert from 0–1 to percentage
    similarity_percentage = similarity * 100

    return round(
        similarity_percentage,
        2
    )


# ------------------------------------------------------------
# Main semantic matching process
# ------------------------------------------------------------

def generate_semantic_matches(
    resume_df,
    job_df,
    model
):

    print("\nPreparing resume text...")

    resume_texts = [
        build_resume_text(row)
        for _, row in resume_df.iterrows()
    ]

    print(
        f"✓ Prepared {len(resume_texts)} resume(s)"
    )

    print("\nPreparing job description text...")

    job_texts = [
        build_job_text(row)
        for _, row in job_df.iterrows()
    ]

    print(
        f"✓ Prepared {len(job_texts)} job descriptions"
    )

    # --------------------------------------------------------
    # Generate embeddings
    # --------------------------------------------------------

    print("\nGenerating resume embeddings...")

    resume_embeddings = model.encode(
        resume_texts,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    print("✓ Resume embeddings generated")

    print("\nGenerating job embeddings...")

    job_embeddings = model.encode(
        job_texts,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    print("✓ Job embeddings generated")

    # --------------------------------------------------------
    # Compare every resume against every job
    # --------------------------------------------------------

    print("\nCalculating semantic similarities...")

    results = []

    for resume_index, resume_row in resume_df.iterrows():

        for job_index, job_row in job_df.iterrows():

            similarity = calculate_similarity(
                resume_embeddings[resume_index],
                job_embeddings[job_index]
            )

            results.append({

                "candidate_id":
                    resume_row["candidate_id"],

                "job_id":
                    job_row["job_id"],

                "job_title":
                    job_row["job_title"],

                "semantic_similarity":
                    similarity
            })

    return pd.DataFrame(results)


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

if __name__ == "__main__":

    print("=" * 70)
    print("AI RESUME INTELLIGENCE SYSTEM")
    print("SEMANTIC SIMILARITY ENGINE")
    print("=" * 70)

    # --------------------------------------------------------
    # Create output directory
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Check input files
    # --------------------------------------------------------

    if not RESUME_FILE.exists():

        raise FileNotFoundError(
            f"Resume dataset not found:\n{RESUME_FILE}"
        )

    if not JOB_FILE.exists():

        raise FileNotFoundError(
            f"Job dataset not found:\n{JOB_FILE}"
        )

    # --------------------------------------------------------
    # Load datasets
    # --------------------------------------------------------

    print("\nLoading datasets...")

    resume_df = pd.read_csv(
        RESUME_FILE
    )

    job_df = pd.read_csv(
        JOB_FILE
    )

    print(
        f"✓ Resumes: {len(resume_df)}"
    )

    print(
        f"✓ Jobs: {len(job_df)}"
    )

    # --------------------------------------------------------
    # Load model
    # --------------------------------------------------------

    model = load_model()

    # --------------------------------------------------------
    # Generate semantic matches
    # --------------------------------------------------------

    results = generate_semantic_matches(
        resume_df,
        job_df,
        model
    )

    # --------------------------------------------------------
    # Save results
    # --------------------------------------------------------

    results.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"\n✓ Results saved to:\n"
        f"{OUTPUT_FILE}"
    )

    # --------------------------------------------------------
    # Display top matches
    # --------------------------------------------------------

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