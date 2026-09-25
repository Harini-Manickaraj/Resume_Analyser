import re
import nltk

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


# ============================================================
# AI BASED RESUME INTELLIGENCE AND JOB RECOMMENDATION SYSTEM
# NLP PREPROCESSING MODULE
# ============================================================

# Download required NLTK resources
def download_nltk_resources():

    resources = [
        ("corpora/stopwords", "stopwords"),
        ("corpora/wordnet", "wordnet"),
        ("corpora/omw-1.4", "omw-1.4")
    ]

    for resource_path, resource_name in resources:

        try:
            nltk.data.find(resource_path)

        except LookupError:
            print(f"Downloading NLTK resource: {resource_name}")
            nltk.download(resource_name)


# Download resources when module is used
download_nltk_resources()


# ------------------------------------------------------------
# Initialize NLP tools
# ------------------------------------------------------------

STOP_WORDS = set(stopwords.words("english"))

LEMMATIZER = WordNetLemmatizer()


# ------------------------------------------------------------
# Clean text
# ------------------------------------------------------------

def clean_text(text):

    if not isinstance(text, str):
        return ""

    # Convert to lowercase
    text = text.lower()

    # Replace common symbols with spaces
    text = re.sub(r"[/|•·]", " ", text)

    # Keep letters, numbers, +, # and basic punctuation
    # This preserves technical terms such as:
    # C++, C#, Python 3, etc.
    text = re.sub(r"[^a-z0-9+#.\s]", " ", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ------------------------------------------------------------
# Tokenization
# ------------------------------------------------------------

def tokenize_text(text):

    cleaned_text = clean_text(text)

    if not cleaned_text:
        return []

    return cleaned_text.split()


# ------------------------------------------------------------
# Remove stopwords
# ------------------------------------------------------------

def remove_stopwords(tokens):

    return [
        token
        for token in tokens
        if token not in STOP_WORDS
    ]


# ------------------------------------------------------------
# Lemmatization
# ------------------------------------------------------------

def lemmatize_tokens(tokens):

    return [
        LEMMATIZER.lemmatize(token)
        for token in tokens
    ]


# ------------------------------------------------------------
# Complete preprocessing pipeline
# ------------------------------------------------------------

def preprocess_text(text):

    # Step 1: Cleaning
    cleaned_text = clean_text(text)

    # Step 2: Tokenization
    tokens = tokenize_text(cleaned_text)

    # Step 3: Stopword removal
    tokens_without_stopwords = remove_stopwords(tokens)

    # Step 4: Lemmatization
    lemmatized_tokens = lemmatize_tokens(
        tokens_without_stopwords
    )

    # Step 5: Final text
    processed_text = " ".join(lemmatized_tokens)

    return {
        "original_text": text,
        "cleaned_text": cleaned_text,
        "tokens": tokens,
        "tokens_without_stopwords": tokens_without_stopwords,
        "lemmatized_tokens": lemmatized_tokens,
        "processed_text": processed_text
    }


# ------------------------------------------------------------
# Test the preprocessing pipeline
# ------------------------------------------------------------

if __name__ == "__main__":

    sample_text = """
    Experienced Data Analyst with strong skills in Python,
    Pandas, NumPy, SQL and Machine Learning.
    Developed data-driven applications and analyzed datasets
    to generate actionable insights.
    """

    result = preprocess_text(sample_text)

    print("\n" + "=" * 60)
    print("NLP PREPROCESSING TEST")
    print("=" * 60)

    print("\nOriginal Text:")
    print(result["original_text"])

    print("\nCleaned Text:")
    print(result["cleaned_text"])

    print("\nTokens:")
    print(result["tokens"])

    print("\nAfter Stopword Removal:")
    print(result["tokens_without_stopwords"])

    print("\nAfter Lemmatization:")
    print(result["lemmatized_tokens"])

    print("\nFinal Processed Text:")
    print(result["processed_text"])

    print("\n" + "=" * 60)
    print("NLP PREPROCESSING COMPLETED")
    print("=" * 60)