import React, { useState, useEffect } from "react";
import { AlertCircle, RefreshCw } from "lucide-react";

import Navbar               from "./components/Navbar";
import ResumeUpload         from "./components/ResumeUpload";
import ScoreCard            from "./components/ScoreCard";
import JobRecommendations   from "./components/JobRecommendations";
import SkillAnalysis        from "./components/SkillAnalysis";
import LearningRecommendations from "./components/LearningRecommendations";

import { analyzeResume, getHealth } from "./services/api";
import "./App.css";

// Loading step labels shown during analysis
const LOADING_STEPS = [
    "Parsing resume content…",
    "Extracting skills & keywords…",
    "Running semantic matching…",
    "Scoring against job profiles…",
    "Generating recommendations…",
];

function App() {
    // ── State ────────────────────────────────────────────────
    const [analysis,      setAnalysis]      = useState(null);
    const [loading,       setLoading]       = useState(false);
    const [error,         setError]         = useState("");
    const [backendOnline, setBackendOnline] = useState(false);
    const [loadingStep,   setLoadingStep]   = useState(0);

    // ── Backend health check ─────────────────────────────────
    useEffect(() => {
        checkBackend();
    }, []);

    const checkBackend = async () => {
        try {
            await getHealth();
            setBackendOnline(true);
        } catch {
            setBackendOnline(false);
        }
    };

    // ── Analyze resume ───────────────────────────────────────
    const handleAnalyze = async (file) => {
        setLoading(true);
        setError("");
        setAnalysis(null);
        setLoadingStep(0);

        // Cycle through loading steps for visual feedback
        const stepInterval = setInterval(() => {
            setLoadingStep((prev) =>
                prev < LOADING_STEPS.length - 1 ? prev + 1 : prev
            );
        }, 900);

        try {
            const result = await analyzeResume(file);
            setAnalysis(result);
        } catch (err) {
            console.error("Resume analysis error:", err);
            let message = "Unable to analyze the resume. Please try again.";
            if (err.response?.data?.detail) {
                message = err.response.data.detail;
            } else if (err.message) {
                message = err.message;
            }
            setError(message);
        } finally {
            clearInterval(stepInterval);
            setLoading(false);
            setLoadingStep(0);
        }
    };

    // ── Reset ────────────────────────────────────────────────
    const resetAnalysis = () => {
        setAnalysis(null);
        setError("");
        window.scrollTo({ top: 0, behavior: "smooth" });
    };

    // ── Skill gap importance → bar width (0–100%) ────────────
    const gapBarWidth = (importance) => {
        const val = Number(importance || 0);
        // Importance values are typically 0–1 floats; scale to %
        const scaled = val <= 1 ? val * 100 : Math.min(val, 100);
        return `${scaled.toFixed(0)}%`;
    };

    // ── Render ───────────────────────────────────────────────
    return (
        <div className="app">
            <Navbar />

            <main className="main-container">

                {/* Backend status pill */}
                <div className={`backend-status ${backendOnline ? "online" : "offline"}`}>
                    <span className={`status-dot${backendOnline ? " pulse" : ""}`} />
                    {backendOnline ? "AI backend connected" : "AI backend unavailable"}
                </div>

                {/* ── Upload / Hero ── */}
                {!analysis && !loading && (
                    <ResumeUpload onAnalyze={handleAnalyze} loading={loading} />
                )}

                {/* ── Error banner — shown above the upload form on failure ── */}
                {error && !loading && (
                    <div className="error-message" role="alert">
                        <AlertCircle size={20} />
                        <div>
                            <strong>Analysis Failed</strong>
                            <p>{error}</p>
                            <button
                                className="error-retry-btn"
                                onClick={() => setError("")}
                            >
                                Dismiss
                            </button>
                        </div>
                    </div>
                )}

                {/* ── Loading overlay ── */}
                {loading && (
                    <div className="loading-overlay">
                        <div className="loading-spinner-ring" aria-hidden="true" />
                        <h3>Analyzing your resume…</h3>
                        <p>
                            Our AI is processing your resume. This usually takes
                            a few seconds.
                        </p>
                        <div className="loading-steps" role="status" aria-live="polite">
                            {LOADING_STEPS.map((step, i) => (
                                <div
                                    key={i}
                                    className={`loading-step${
                                        i === loadingStep ? " active" :
                                        i < loadingStep  ? " done"   : ""
                                    }`}
                                >
                                    <span className="loading-step-dot" />
                                    {step}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* ── Dashboard ── */}
                {analysis && !loading && (
                    <div className="dashboard">

                        {/* Dashboard header */}
                        <div className="dashboard-header">
                            <div className="dashboard-header-text">
                                <p className="eyebrow">AI RESUME REPORT</p>
                                <h1>Resume Analysis</h1>
                                <p>
                                    Your AI-powered resume intelligence report is ready.
                                </p>
                            </div>
                            <button
                                className="new-analysis-button"
                                onClick={resetAnalysis}
                                aria-label="Start a new resume analysis"
                            >
                                <RefreshCw size={16} />
                                Analyze Another Resume
                            </button>
                        </div>

                        {/* Score */}
                        <ScoreCard analysis={analysis} />

                        {/* Skills */}
                        <SkillAnalysis skills={analysis.skills} />

                        {/* Jobs */}
                        <JobRecommendations
                            jobs={analysis.job_recommendations || []}
                        />

                        {/* Learning */}
                        <LearningRecommendations
                            recommendations={analysis.learning_recommendations || []}
                        />

                        {/* Skill gaps */}
                        {analysis.skill_gaps && analysis.skill_gaps.length > 0 && (
                            <section className="dashboard-section">
                                <div className="section-title">
                                    <div>
                                        <p className="eyebrow">PRIORITY AREAS</p>
                                        <h2>Skill Gap Priority</h2>
                                    </div>
                                    <span className="result-count">
                                        {analysis.skill_gaps.length}{" "}
                                        {analysis.skill_gaps.length === 1 ? "gap" : "gaps"}
                                    </span>
                                </div>

                                <div className="gap-list">
                                    {analysis.skill_gaps.map((gap, index) => {
                                        const importance = Number(gap.importance || 0);
                                        return (
                                            <div className="gap-item" key={index}>
                                                <div className="gap-item-left">
                                                    <div className="gap-index">
                                                        {index + 1}
                                                    </div>
                                                    <div>
                                                        <strong>{gap.skill}</strong>
                                                        <div className="gap-item-label">
                                                            Skill gap · Priority area
                                                        </div>
                                                    </div>
                                                </div>

                                                <div className="gap-score">
                                                    <div className="gap-bar-track">
                                                        <div
                                                            className="gap-bar-fill"
                                                            style={{ width: gapBarWidth(importance) }}
                                                        />
                                                    </div>
                                                    <span className="gap-score-value">
                                                        {importance.toFixed(2)}
                                                    </span>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            </section>
                        )}

                    </div>
                )}

            </main>

            {/* Footer */}
            <footer className="footer">
                <p>ResumeIQ · AI Resume Intelligence</p>
                <span>
                    Resume analysis &nbsp;·&nbsp; Semantic matching &nbsp;·&nbsp; Job recommendation
                </span>
            </footer>
        </div>
    );
}

export default App;
