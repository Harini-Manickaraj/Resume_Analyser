import React from "react";
import { BriefcaseBusiness, ArrowUpRight, MapPin, Building2 } from "lucide-react";

// Classify match percentage into tier
function getMatchTier(score) {
    if (score >= 70) return "high";
    if (score >= 40) return "medium";
    return "low";
}

function JobRecommendations({ jobs = [] }) {
    return (
        <section className="dashboard-section">
            <div className="section-title">
                <div>
                    <p className="eyebrow">JOB MATCHING</p>
                    <h2>Recommended Jobs</h2>
                </div>
                <span className="result-count">
                    {jobs.length} {jobs.length === 1 ? "match" : "matches"}
                </span>
            </div>

            {jobs.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-state-icon">
                        <BriefcaseBusiness size={26} />
                    </div>
                    <p>No job recommendations available yet.</p>
                </div>
            ) : (
                <div className="job-list">
                    {jobs.map((job, index) => {
                        const score = Number(job.match_percentage || 0);
                        const tier  = getMatchTier(score);
                        const label = job.classification || (
                            tier === "high"   ? "Excellent Match" :
                            tier === "medium" ? "Good Match"      : "Partial Match"
                        );

                        return (
                            <div
                                className="job-card"
                                key={job.job_id || index}
                                role="listitem"
                            >
                                {/* Rank badge */}
                                <div className={`job-rank${index === 0 ? " top" : ""}`}>
                                    #{index + 1}
                                </div>

                                {/* Icon */}
                                <div className="job-icon">
                                    <BriefcaseBusiness size={18} />
                                </div>

                                {/* Title + progress */}
                                <div className="job-info">
                                    <h3>{job.job_title || "Unknown Position"}</h3>
                                    <div className="job-info-meta">
                                        {job.job_id || "JOB"}
                                    </div>
                                    <div className="progress-bar">
                                        <div
                                            className={`progress-fill ${tier}`}
                                            style={{ width: `${Math.min(score, 100)}%` }}
                                            role="progressbar"
                                            aria-valuenow={score}
                                            aria-valuemin={0}
                                            aria-valuemax={100}
                                        />
                                    </div>
                                </div>

                                {/* Score + label */}
                                <div className="job-score">
                                    <strong>{score.toFixed(1)}%</strong>
                                    <span className={`job-score-label ${tier}`}>
                                        {label}
                                    </span>
                                </div>

                                <ArrowUpRight size={18} className="job-arrow" />
                            </div>
                        );
                    })}
                </div>
            )}
        </section>
    );
}

export default JobRecommendations;
