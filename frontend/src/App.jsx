import React, {
    useState,
    useEffect
} from "react";

import {
    AlertCircle,
    RefreshCw
} from "lucide-react";


import Navbar from "./components/Navbar";

import ResumeUpload
    from "./components/ResumeUpload";

import ScoreCard
    from "./components/ScoreCard";

import JobRecommendations
    from "./components/JobRecommendations";

import SkillAnalysis
    from "./components/SkillAnalysis";

import LearningRecommendations
    from "./components/LearningRecommendations";


import {
    analyzeResume,
    getHealth
} from "./services/api";


function App() {

    // ========================================================
    // STATE
    // ========================================================

    const [
        analysis,
        setAnalysis
    ] = useState(null);


    const [
        loading,
        setLoading
    ] = useState(false);


    const [
        error,
        setError
    ] = useState("");


    const [
        backendOnline,
        setBackendOnline
    ] = useState(false);


    // ========================================================
    // CHECK BACKEND
    // ========================================================

    useEffect(() => {

        checkBackend();

    }, []);


    const checkBackend = async () => {

        try {

            await getHealth();

            setBackendOnline(true);

        } catch (error) {

            setBackendOnline(false);
        }
    };


    // ========================================================
    // ANALYZE RESUME
    // ========================================================

    const handleAnalyze = async (
        file
    ) => {

        setLoading(true);

        setError("");

        setAnalysis(null);


        try {

            const result =
                await analyzeResume(file);


            setAnalysis(result);

        } catch (error) {

            console.error(
                "Resume analysis error:",
                error
            );


            let message =
                "Unable to analyze the resume.";


            if (
                error.response &&
                error.response.data
            ) {

                const detail =
                    error.response.data.detail;

                if (detail) {
                    message = detail;
                }

            } else if (
                error.message
            ) {

                message =
                    error.message;
            }


            setError(message);

        } finally {

            setLoading(false);
        }
    };


    // ========================================================
    // NEW ANALYSIS
    // ========================================================

    const resetAnalysis = () => {

        setAnalysis(null);

        setError("");

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    };


    // ========================================================
    // RENDER
    // ========================================================

    return (

        <div className="app">

            <Navbar />


            <main className="main-container">


                {/* ==========================================
                    BACKEND STATUS
                =========================================== */}

                <div
                    className={
                        `backend-status ${
                            backendOnline
                                ? "online"
                                : "offline"
                        }`
                    }
                >

                    <span className="status-dot" />

                    {backendOnline
                        ? "AI backend connected"
                        : "AI backend unavailable"}

                </div>


                {/* ==========================================
                    UPLOAD
                =========================================== */}

                {!analysis && (

                    <ResumeUpload
                        onAnalyze={
                            handleAnalyze
                        }
                        loading={
                            loading
                        }
                    />

                )}


                {/* ==========================================
                    ERROR
                =========================================== */}

                {error && (

                    <div className="error-message">

                        <AlertCircle
                            size={22}
                        />

                        <div>

                            <strong>
                                Analysis Failed
                            </strong>

                            <p>
                                {error}
                            </p>

                        </div>

                    </div>

                )}


                {/* ==========================================
                    DASHBOARD
                =========================================== */}

                {analysis && (

                    <div className="dashboard">


                        {/* HEADER */}

                        <div className="dashboard-header">

                            <div>

                                <p className="eyebrow">
                                    AI RESUME REPORT
                                </p>

                                <h1>
                                    Resume Analysis
                                </h1>

                                <p>
                                    Here is your AI-powered
                                    resume intelligence report.
                                </p>

                            </div>


                            <button
                                className="new-analysis-button"
                                onClick={
                                    resetAnalysis
                                }
                            >

                                <RefreshCw
                                    size={18}
                                />

                                Analyze Another Resume

                            </button>

                        </div>


                        {/* SCORE */}

                        <ScoreCard
                            analysis={
                                analysis
                            }
                        />


                        {/* SKILLS */}

                        <SkillAnalysis
                            skills={
                                analysis.skills
                            }
                        />


                        {/* JOBS */}

                        <JobRecommendations
                            jobs={
                                analysis.job_recommendations ||
                                []
                            }
                        />


                        {/* LEARNING */}

                        <LearningRecommendations
                            recommendations={
                                analysis.learning_recommendations ||
                                []
                            }
                        />


                        {/* SKILL GAPS */}

                        {analysis.skill_gaps &&
                            analysis.skill_gaps.length > 0 && (

                                <section className="dashboard-section">

                                    <div className="section-title">

                                        <div>

                                            <p className="eyebrow">
                                                PRIORITY AREAS
                                            </p>

                                            <h2>
                                                Skill Gap Priority
                                            </h2>

                                        </div>

                                    </div>


                                    <div className="gap-list">

                                        {analysis.skill_gaps.map(
                                            (
                                                gap,
                                                index
                                            ) => (

                                                <div
                                                    className="gap-item"
                                                    key={index}
                                                >

                                                    <div>

                                                        <strong>
                                                            {
                                                                gap.skill
                                                            }
                                                        </strong>

                                                        <span>
                                                            Importance
                                                        </span>

                                                    </div>


                                                    <div className="gap-score">

                                                        {Number(
                                                            gap.importance ||
                                                            0
                                                        ).toFixed(2)}

                                                    </div>

                                                </div>

                                            )
                                        )}

                                    </div>

                                </section>

                            )}


                    </div>

                )}

            </main>


            {/* ================================================
                FOOTER
            ================================================= */}

            <footer className="footer">

                <p>
                    AI Resume Intelligence
                </p>

                <span>
                    Resume analysis • Semantic matching
                    • Job recommendation
                </span>

            </footer>

        </div>
    );
}


export default App;