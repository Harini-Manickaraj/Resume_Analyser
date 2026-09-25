import React from "react";
import { BookOpen, ArrowRight, GraduationCap } from "lucide-react";

function LearningRecommendations({ recommendations = [] }) {
    return (
        <section className="dashboard-section">
            <div className="section-title">
                <div>
                    <p className="eyebrow">CAREER DEVELOPMENT</p>
                    <h2>Learning Recommendations</h2>
                </div>
                {recommendations.length > 0 && (
                    <span className="result-count">
                        {recommendations.length} {recommendations.length === 1 ? "skill" : "skills"}
                    </span>
                )}
            </div>

            {recommendations.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-state-icon">
                        <BookOpen size={26} />
                    </div>
                    <p>No learning recommendations available.</p>
                </div>
            ) : (
                <div className="learning-grid">
                    {recommendations.map((item, index) => (
                        <div className="learning-card" key={index}>
                            <div className="learning-card-header">
                                <div className="learning-icon">
                                    <BookOpen size={18} />
                                </div>
                                <span className="learning-card-index">
                                    #{String(index + 1).padStart(2, "0")}
                                </span>
                            </div>

                            <div className="learning-content">
                                <h3>{item.skill}</h3>
                                <p>
                                    {item.reason ||
                                        "Recommended to improve your job match score and expand your skill set."}
                                </p>
                            </div>

                            <div className="learning-action">
                                <span>Explore resources</span>
                                <ArrowRight size={14} />
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </section>
    );
}

export default LearningRecommendations;
