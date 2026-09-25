import React from "react";

import {
    Target,
    GraduationCap,
    Briefcase
} from "lucide-react";


function ScoreCard({
    analysis
}) {

    if (!analysis) {
        return null;
    }


    const score =
        Number(
            analysis.overall_score || 0
        );


    const candidate =
        analysis.candidate || {};


    const classification =
        analysis.classification ||
        "Not Available";


    return (

        <section className="dashboard-section">

            <div className="section-title">

                <div>

                    <p className="eyebrow">
                        ANALYSIS RESULT
                    </p>

                    <h2>
                        Resume Intelligence Score
                    </h2>

                </div>

            </div>


            <div className="score-grid">

                {/* SCORE */}

                <div className="score-card main-score">

                    <div className="score-ring">

                        <div>

                            <strong>
                                {score.toFixed(1)}
                            </strong>

                            <span>
                                %
                            </span>

                        </div>

                    </div>


                    <div className="score-content">

                        <span>
                            Overall Match
                        </span>

                        <h3>
                            {classification}
                        </h3>

                        <p>
                            Based on skills, semantic
                            similarity, education,
                            experience and project relevance.
                        </p>

                    </div>

                </div>


                {/* EDUCATION */}

                <div className="info-card">

                    <div className="info-card-icon">
                        <GraduationCap size={22} />
                    </div>

                    <div>

                        <span>
                            Education
                        </span>

                        <strong>
                            {candidate.education ||
                                "Not detected"}
                        </strong>

                    </div>

                </div>


                {/* EXPERIENCE */}

                <div className="info-card">

                    <div className="info-card-icon">
                        <Briefcase size={22} />
                    </div>

                    <div>

                        <span>
                            Experience
                        </span>

                        <strong>
                            {candidate.experience ?? 0}
                            {" "}
                            years
                        </strong>

                    </div>

                </div>


                {/* TARGET */}

                <div className="info-card">

                    <div className="info-card-icon">
                        <Target size={22} />
                    </div>

                    <div>

                        <span>
                            Candidate
                        </span>

                        <strong>
                            {candidate.name ||
                                "Candidate"}
                        </strong>

                    </div>

                </div>

            </div>

        </section>
    );
}


export default ScoreCard;