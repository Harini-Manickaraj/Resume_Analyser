"""
API Routes
AI Based Resume Intelligence and Job Recommendation System
"""

from pathlib import Path
import tempfile
import shutil

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
)

from backend.parsers.resume_parser import (
    parse_resume,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api",
    tags=["AI Resume Intelligence"]
)


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DATA_DIR = PROJECT_ROOT / "data"

DATASET_DIR = DATA_DIR / "datasets"

PROCESSED_DIR = DATASET_DIR / "processed"

UPLOAD_DIR = DATA_DIR / "resumes"

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# BASIC API
# ============================================================

@router.get("/")
def api_root():

    return {
        "application": "AI Resume Intelligence API",
        "version": "1.0.0",
        "status": "running"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@router.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "AI Resume Intelligence API"
    }


# ============================================================
# HELPER — READ CSV
# ============================================================

def read_csv_file(filename):

    import pandas as pd

    file_path = PROCESSED_DIR / filename

    if not file_path.exists():

        return []

    try:

        df = pd.read_csv(
            file_path
        )

        # Replace NaN values
        df = df.fillna("")

        return df.to_dict(
            orient="records"
        )

    except Exception:

        return []


# ============================================================
# GET RESUMES
# ============================================================

@router.get("/resumes")
def get_resumes():

    resume_file = DATASET_DIR / "resume_profiles.csv"

    if not resume_file.exists():

        return {
            "resumes": []
        }

    import pandas as pd

    try:

        df = pd.read_csv(
            resume_file
        )

        df = df.fillna("")

        return {
            "resumes": df.to_dict(
                orient="records"
            )
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Could not load resumes: {str(exc)}"
        )


# ============================================================
# GET JOBS
# ============================================================

@router.get("/jobs")
def get_jobs():

    job_file = DATASET_DIR / "job_descriptions.csv"

    if not job_file.exists():

        return {
            "jobs": []
        }

    import pandas as pd

    try:

        df = pd.read_csv(
            job_file
        )

        df = df.fillna("")

        return {
            "jobs": df.to_dict(
                orient="records"
            )
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Could not load jobs: {str(exc)}"
        )


# ============================================================
# GET MATCHING RESULTS
# ============================================================

@router.get("/matching")
def get_matching():

    results = read_csv_file(
        "hybrid_matching_results.csv"
    )

    return {
        "matching_results": results
    }


# ============================================================
# GET RECOMMENDATIONS
# ============================================================

@router.get("/recommendations")
def get_recommendations():

    results = read_csv_file(
        "job_recommendations.csv"
    )

    return {
        "recommendations": results
    }


# ============================================================
# GET SKILL GAPS
# ============================================================

@router.get("/skill-gaps")
def get_skill_gaps():

    results = read_csv_file(
        "skill_gap_analysis.csv"
    )

    return {
        "skill_gaps": results
    }


# ============================================================
# GET LEARNING RECOMMENDATIONS
# ============================================================

@router.get("/learning")
def get_learning():

    results = read_csv_file(
        "learning_recommendations.csv"
    )

    return {
        "learning_recommendations": results
    }


# ============================================================
# GET CANDIDATE
# ============================================================

@router.get("/candidate/{candidate_id}")
def get_candidate(
    candidate_id: str
):

    resume_file = DATASET_DIR / "resume_profiles.csv"

    if not resume_file.exists():

        raise HTTPException(
            status_code=404,
            detail="Resume dataset not found."
        )

    import pandas as pd

    try:

        df = pd.read_csv(
            resume_file
        )

        df = df.fillna("")

        candidate = df[
            df["candidate_id"].astype(str)
            == str(candidate_id)
        ]

        if candidate.empty:

            raise HTTPException(
                status_code=404,
                detail=f"Candidate {candidate_id} not found."
            )

        return candidate.iloc[0].to_dict()

    except HTTPException:

        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Could not load candidate: {str(exc)}"
        )


# ============================================================
# RESUME UPLOAD
# ============================================================

@router.post("/resume/upload")
async def upload_resume(
    file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # Validate filename
    # --------------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No filename provided."
        )

    # --------------------------------------------------------
    # Validate extension
    # --------------------------------------------------------

    extension = Path(
        file.filename
    ).suffix.lower()

    allowed_extensions = {
        ".pdf",
        ".docx"
    }

    if extension not in allowed_extensions:

        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX resumes are supported."
        )

    # --------------------------------------------------------
    # Create upload path
    # --------------------------------------------------------

    safe_filename = Path(
        file.filename
    ).name

    upload_path = UPLOAD_DIR / safe_filename

    # --------------------------------------------------------
    # Save file
    # --------------------------------------------------------

    try:

        with open(
            upload_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Could not save resume: {str(exc)}"
        )

    return {

        "message": "Resume uploaded successfully.",

        "filename": safe_filename,

        "file_path": str(
            upload_path
        )
    }


# ============================================================
# RESUME ANALYSIS
# ============================================================

@router.post("/resume/analyze")
async def analyze_resume(
    file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # Validate filename
    # --------------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No resume file provided."
        )

    # --------------------------------------------------------
    # Validate extension
    # --------------------------------------------------------

    extension = Path(
        file.filename
    ).suffix.lower()

    allowed_extensions = {
        ".pdf",
        ".docx"
    }

    if extension not in allowed_extensions:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file format. "
                "Please upload a PDF or DOCX resume."
            )
        )

    # --------------------------------------------------------
    # Create temporary file
    # --------------------------------------------------------

    temporary_path = None

    try:

        # ----------------------------------------------------
        # Create temporary file with correct extension
        # ----------------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension
        ) as temporary_file:

            temporary_path = Path(
                temporary_file.name
            )

            # ------------------------------------------------
            # IMPORTANT:
            # Save uploaded BYTES to temporary FILE
            # ------------------------------------------------

            content = await file.read()

            temporary_file.write(
                content
            )

        # ----------------------------------------------------
        # Make sure file exists
        # ----------------------------------------------------

        if not temporary_path.exists():

            raise RuntimeError(
                "Temporary resume file could not be created."
            )

        # ----------------------------------------------------
        # Parse resume using FILE PATH
        # ----------------------------------------------------

        try:

            parsed_resume = parse_resume(
                temporary_path
            )

        except Exception as exc:

            raise HTTPException(
                status_code=500,
                detail=f"Resume parsing failed: {str(exc)}"
            )

        # ----------------------------------------------------
        # Import analysis engine
        # ----------------------------------------------------

        try:

            from backend.analysis.resume_analyzer import (
                analyze_resume as run_resume_analysis
            )

        except ImportError as exc:

            raise HTTPException(
                status_code=500,
                detail=(
                    "Could not import the resume analysis engine: "
                    f"{str(exc)}"
                )
            )

        # ----------------------------------------------------
        # Run analysis
        # ----------------------------------------------------

        try:

            result = run_resume_analysis(
                parsed_resume
            )

        except TypeError:

            # ------------------------------------------------
            # Compatibility fallback:
            # Some versions of the analyzer expect raw text.
            # ------------------------------------------------

            try:

                result = run_resume_analysis(
                    parsed_resume.get(
                        "raw_text",
                        ""
                    )
                )

            except Exception as exc:

                raise HTTPException(
                    status_code=500,
                    detail=(
                        "Resume analysis failed: "
                        f"{str(exc)}"
                    )
                )

        except Exception as exc:

            raise HTTPException(
                status_code=500,
                detail=(
                    "Resume analysis failed: "
                    f"{str(exc)}"
                )
            )

        # ----------------------------------------------------
        # Return final response
        # ----------------------------------------------------

        return {

            "success": True,

            "filename": file.filename,

            "resume": parsed_resume,

            "analysis": result
        }

    except HTTPException:

        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )

    finally:

        # ----------------------------------------------------
        # Remove temporary file
        # ----------------------------------------------------

        if temporary_path:

            try:

                if temporary_path.exists():

                    temporary_path.unlink()

            except Exception:

                pass