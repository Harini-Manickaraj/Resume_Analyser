"""
Resume Parser
AI Based Resume Intelligence and Job Recommendation System

Supports:
    PDF
    DOCX

Supports input as:
    - File path
    - pathlib.Path
    - Raw extracted resume text
    - Parsed resume dictionary
"""

from pathlib import Path
import re


# ============================================================
# PDF EXTRACTION
# ============================================================

def extract_pdf_text(file_path):
    """Extract text from a PDF file."""

    try:
        import pymupdf

        document = pymupdf.open(str(file_path))

        text_parts = []

        for page in document:
            page_text = page.get_text()

            if page_text:
                text_parts.append(page_text)

        document.close()

        return "\n".join(text_parts).strip()

    except ImportError:

        import fitz

        document = fitz.open(str(file_path))

        text_parts = []

        for page in document:
            page_text = page.get_text()

            if page_text:
                text_parts.append(page_text)

        document.close()

        return "\n".join(text_parts).strip()


# ============================================================
# DOCX EXTRACTION
# ============================================================

def extract_docx_text(file_path):
    """Extract text from DOCX."""

    from docx import Document

    document = Document(str(file_path))

    text_parts = []

    for paragraph in document.paragraphs:

        text = paragraph.text.strip()

        if text:
            text_parts.append(text)

    # Also extract table content
    for table in document.tables:

        for row in table.rows:

            cells = []

            for cell in row.cells:

                cell_text = cell.text.strip()

                if cell_text:
                    cells.append(cell_text)

            if cells:
                text_parts.append(
                    " | ".join(cells)
                )

    return "\n".join(text_parts).strip()


# ============================================================
# FILE → TEXT
# ============================================================

def extract_resume_text(file_path):
    """
    Extract resume text from PDF or DOCX.

    IMPORTANT:
    This function expects an actual file path.
    """

    file_path = Path(file_path)

    if not file_path.exists():

        raise FileNotFoundError(
            f"Resume file not found: {file_path}"
        )

    extension = file_path.suffix.lower()

    if extension == ".pdf":

        text = extract_pdf_text(file_path)

    elif extension == ".docx":

        text = extract_docx_text(file_path)

    else:

        raise ValueError(
            "Unsupported resume format. "
            "Only PDF and DOCX files are supported."
        )

    if not text.strip():

        raise ValueError(
            "No readable text was found in the resume."
        )

    return text


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_resume_text(text):
    """Normalize extracted resume text."""

    if not text:
        return ""

    text = str(text)

    text = text.replace(
        "\r\n",
        "\n"
    )

    text = text.replace(
        "\r",
        "\n"
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


# ============================================================
# SECTION ALIASES
# ============================================================

SECTION_ALIASES = {

    "summary": [
        "summary",
        "professional summary",
        "profile",
        "career objective",
        "objective",
        "about me"
    ],

    "education": [
        "education",
        "academic background",
        "educational qualification",
        "educational qualifications",
        "qualifications"
    ],

    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "internship",
        "internships"
    ],

    "skills": [
        "skills",
        "technical skills",
        "technical skill",
        "core skills",
        "technologies",
        "technical expertise",
        "skills and technologies"
    ],

    "projects": [
        "projects",
        "academic projects",
        "personal projects",
        "project experience"
    ],

    "certifications": [
        "certifications",
        "certificates",
        "licenses"
    ],

    "achievements": [
        "achievements",
        "accomplishments",
        "awards",
        "honors"
    ],

    "interests": [
        "interests",
        "areas of interest",
        "hobbies",
        "area of interests"
    ],

    "soft_skills": [
        "soft skills",
        "personal skills",
        "strengths"
    ],

    "position": [
        "position of responsibility",
        "positions of responsibility",
        "responsibility"
    ]
}


# ============================================================
# HEADING NORMALIZATION
# ============================================================

def normalize_heading(line):

    line = line.strip()

    line = re.sub(
        r"^[•●▪◦\-–—*]+\s*",
        "",
        line
    )

    line = line.rstrip(":")

    line = re.sub(
        r"\s+",
        " ",
        line
    )

    return line.strip().lower()


# ============================================================
# DETECT SECTION
# ============================================================

def detect_section(line):

    normalized = normalize_heading(line)

    if not normalized:
        return None

    for section_name, aliases in SECTION_ALIASES.items():

        for alias in aliases:

            if normalized == alias:
                return section_name

    return None


# ============================================================
# EXTRACT SECTIONS
# ============================================================

def extract_sections(text):

    text = normalize_resume_text(text)

    lines = text.splitlines()

    sections = {
        "summary": [],
        "education": [],
        "experience": [],
        "skills": [],
        "projects": [],
        "certifications": [],
        "achievements": [],
        "interests": [],
        "soft_skills": [],
        "position": [],
        "other": []
    }

    current_section = "other"

    for line in lines:

        line = line.strip()

        if not line:
            continue

        detected = detect_section(line)

        if detected:

            current_section = detected

        else:

            sections[current_section].append(
                line
            )

    return {
        key: "\n".join(value).strip()
        for key, value in sections.items()
    }


# ============================================================
# NAME EXTRACTION
# ============================================================

def extract_name(text):

    lines = [
        line.strip()
        for line in str(text).splitlines()
        if line.strip()
    ]

    if not lines:
        return "Candidate"

    ignored = {
        "resume",
        "curriculum vitae",
        "cv",
        "profile"
    }

    for line in lines[:10]:

        cleaned = line.strip(
            " :-|"
        )

        if not cleaned:
            continue

        if cleaned.lower() in ignored:
            continue

        if "@" in cleaned:
            continue

        if re.search(
            r"\b(phone|mobile|email|linkedin|github)\b",
            cleaned,
            re.IGNORECASE
        ):
            continue

        if len(cleaned.split()) > 6:
            continue

        return cleaned

    return "Candidate"


# ============================================================
# EXPERIENCE YEARS
# ============================================================

def extract_experience_years(text):

    patterns = [

        r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s+of\s+experience",

        r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s+experience",

        r"experience\s*[:\-]\s*(\d+(?:\.\d+)?)\s*\+?\s*years?"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            str(text),
            re.IGNORECASE
        )

        if match:

            try:
                return float(
                    match.group(1)
                )

            except ValueError:
                pass

    return 0


# ============================================================
# CREATE PROFILE FROM TEXT
# ============================================================

def create_profile_from_text(text):

    text = normalize_resume_text(
        text
    )

    sections = extract_sections(
        text
    )

    name = extract_name(
        text
    )

    profile = {

        "name": name,

        "candidate_name": name,

        "raw_text": text,

        "summary": sections.get(
            "summary",
            ""
        ),

        "education": sections.get(
            "education",
            ""
        ),

        "experience": sections.get(
            "experience",
            ""
        ),

        "skills": sections.get(
            "skills",
            ""
        ),

        "projects": sections.get(
            "projects",
            ""
        ),

        "certifications": sections.get(
            "certifications",
            ""
        ),

        "achievements": sections.get(
            "achievements",
            ""
        ),

        "interests": sections.get(
            "interests",
            ""
        ),

        "soft_skills": sections.get(
            "soft_skills",
            ""
        ),

        "position": sections.get(
            "position",
            ""
        ),

        "other": sections.get(
            "other",
            ""
        ),

        "experience_years":
            extract_experience_years(
                text
            )
    }

    return profile


# ============================================================
# PARSE RESUME
# ============================================================

def parse_resume(resume_input):

    """
    Parse a resume.

    Accepts:
        - PDF path
        - DOCX path
        - Raw resume text
        - pathlib.Path
    """

    # --------------------------------------------------------
    # Dictionary input
    # --------------------------------------------------------

    if isinstance(
        resume_input,
        dict
    ):

        return create_resume_profile(
            resume_input
        )

    # --------------------------------------------------------
    # Path input
    # --------------------------------------------------------

    if isinstance(
        resume_input,
        Path
    ):

        text = extract_resume_text(
            resume_input
        )

        return create_profile_from_text(
            text
        )

    # --------------------------------------------------------
    # String input
    # --------------------------------------------------------

    if isinstance(
        resume_input,
        str
    ):

        # IMPORTANT:
        # A large string containing newlines is
        # resume text, NOT a filename.

        if (
            "\n" in resume_input
            or "\r" in resume_input
        ):

            return create_profile_from_text(
                resume_input
            )

        # Otherwise check whether it is a real file

        possible_path = Path(
            resume_input
        )

        if possible_path.exists():

            text = extract_resume_text(
                possible_path
            )

            return create_profile_from_text(
                text
            )

        # Short strings can still be raw text
        # instead of file paths.

        return create_profile_from_text(
            resume_input
        )

    # --------------------------------------------------------
    # Unsupported type
    # --------------------------------------------------------

    raise TypeError(
        "resume_input must be a file path, "
        "Path object, raw text, or dictionary."
    )


# ============================================================
# CREATE RESUME PROFILE
# ============================================================

def create_resume_profile(resume_input):

    """
    Create a normalized resume profile.

    Accepts:
        - file path
        - Path
        - raw resume text
        - dictionary
    """

    # --------------------------------------------------------
    # Already a dictionary
    # --------------------------------------------------------

    if isinstance(
        resume_input,
        dict
    ):

        profile = dict(
            resume_input
        )

    # --------------------------------------------------------
    # Path
    # --------------------------------------------------------

    elif isinstance(
        resume_input,
        Path
    ):

        profile = parse_resume(
            resume_input
        )

    # --------------------------------------------------------
    # String
    # --------------------------------------------------------

    elif isinstance(
        resume_input,
        str
    ):

        # If it contains newline characters,
        # it is definitely extracted resume text.

        if (
            "\n" in resume_input
            or "\r" in resume_input
        ):

            profile = create_profile_from_text(
                resume_input
            )

        else:

            possible_path = Path(
                resume_input
            )

            if possible_path.exists():

                profile = parse_resume(
                    possible_path
                )

            else:

                # Treat as raw text instead of
                # throwing "file not found".

                profile = create_profile_from_text(
                    resume_input
                )

    else:

        raise TypeError(
            "resume_input must be a file path, "
            "Path object, raw text, or dictionary."
        )

    # --------------------------------------------------------
    # Required fields
    # --------------------------------------------------------

    defaults = {

        "name": "Candidate",

        "candidate_name": "Candidate",

        "raw_text": "",

        "summary": "",

        "education": "",

        "experience": "",

        "skills": "",

        "projects": "",

        "certifications": "",

        "achievements": "",

        "interests": "",

        "soft_skills": "",

        "position": "",

        "other": "",

        "experience_years": 0
    }

    for key, default in defaults.items():

        if (
            key not in profile
            or profile[key] is None
        ):

            profile[key] = default

    # --------------------------------------------------------
    # Name consistency
    # --------------------------------------------------------

    if not profile.get("name"):

        profile["name"] = profile.get(
            "candidate_name",
            "Candidate"
        )

    if (
        profile["name"] == "Candidate"
        and profile.get("candidate_name")
    ):

        profile["name"] = profile[
            "candidate_name"
        ]

    profile["candidate_name"] = profile[
        "name"
    ]

    # --------------------------------------------------------
    # Experience
    # --------------------------------------------------------

    try:

        profile["experience_years"] = float(
            profile.get(
                "experience_years",
                0
            )
        )

    except (
        ValueError,
        TypeError
    ):

        profile["experience_years"] = 0

    return profile


# ============================================================
# BACKWARD COMPATIBILITY ALIASES
# ============================================================

def get_resume_text(file_path):

    return extract_resume_text(
        file_path
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        "======================================"
    )

    print(
        "Resume Parser Test"
    )

    print(
        "======================================"
    )

    print(
        "extract_resume_text()      OK"
    )

    print(
        "parse_resume()             OK"
    )

    print(
        "create_resume_profile()    OK"
    )

    print(
        "create_profile_from_text() OK"
    )

    print(
        "======================================"
    )