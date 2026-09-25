from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router


# =========================================================
# CREATE FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="AI Resume Intelligence API",

    description=(
        "AI-based Resume Intelligence and "
        "Job Recommendation System"
    ),

    version="1.0.0"
)


# =========================================================
# CORS CONFIGURATION
# =========================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "*"
    ],

    allow_credentials=True,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ]
)


# =========================================================
# REGISTER API ROUTES
# =========================================================

app.include_router(
    router
)


# =========================================================
# ROOT ENDPOINT
# =========================================================

@app.get("/")
def root():

    return {

        "application": (
            "AI Resume Intelligence"
        ),

        "version": "1.0.0",

        "status": "running",

        "documentation": "/docs"
    }