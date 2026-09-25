import React from "react";
import { GraduationCap, Briefcase, User } from "lucide-react";

// Classify score into tier
function getScoreTier(score) {
    if (score >= 70) return "high";
    if (score >= 40) return "medium";
    return "low";
}

// SVG circular progress ring
function ScoreRing({ score }) {
    const radius = 64;
    const stroke = 10;
    const normalizedR = radius - stroke / 2;
    const circumference = 2 * Math.PI * normalizedR;
    const clampedScore = Math.min(Math.max(score, 0), 100);
    const offset = circumference - (clampedScore / 100) * circumference;
    const tier = getScoreTier(clampedScore);

    return (
        <div className="score-ring-wrapper">
            <svg width={radius * 2} height={radius * 2}>
                <circle
                    className="score-ring-bg"
                    cx={radius}
                    cy={radius}
                    r={normalizedR}
                    strokeWidth={stroke}
                />
                <circle
                    className={`score-ring-fill ${tier}`}
                    cx={radius}
                    cy={radius}
                    r={normalizedR}
                    strokeWidth={stroke}
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                />
            </svg>
            <div className="score-ring-center">
                <span className="score-ring-value">{clampedScore.toFixed(0)}</span>
                <span className="score-ring-unit">/ 100</span>
            </div>
        </div>
    );
}

function ScoreCard({ analysis }) {
    if (!analysis) return null;

    const score          = Number(analysis.overall_score || 0);
    const candidate      = analysis.candidate || {};
    const classification = analysis.classification || "Not Available";
    const tier           = getScoreTier(score);

    return (
        <section className="dashboard-section">
            <div className="section-title">
                <div>
                    <p className="eyebrow">ANALYSIS RESULT</p>
                    <h2>Resume Intelligence Score</h2>
                </div>
            </div>

            <div className="score-grid">
                {/* Circular score */}
                <div className="main-score">
                    <ScoreRing score={score} />
                    <div>
                        <div className={`score-classification ${tier}`}>
                            {classification}
                        </div>
                        <p className="score-desc">
                            Based on skills, semantic similarity,
                            education, experience and project relevance.
                        </p>
                    </div>
                </div>

                {/* Candidate name */}
                <div className="info-card">
                    <div className="info-card-icon">
                        <User size={19} />
                    </div>
                    <div>
                        <div className="info-card-label">Candidate</div>
                        <div className="info-card-value">
                            {candidate.name || "Not detected"}
                        </div>
                    </div>
                </div>

                {/* Education */}
                <div className="info-card">
                    <div className="info-card-icon">
                        <GraduationCap size={19} />
                    </div>
                    <div>
                        <div className="info-card-label">Education</div>
                        <div className="info-card-value">
                            {candidate.education || "Not detected"}
                        </div>
                    </div>
                </div>

                {/* Experience */}
                <div className="info-card">
                    <div className="info-card-icon">
                        <Briefcase size={19} />
                    </div>
                    <div>
                        <div className="info-card-label">Experience</div>
                        <div className="info-card-value">
                            {candidate.experience ?? 0}{" "}
                            {Number(candidate.experience) === 1 ? "year" : "years"}
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}

export default ScoreCard;
