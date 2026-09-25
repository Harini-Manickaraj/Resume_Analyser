import React from "react";

import {
    BookOpen,
    ArrowRight
} from "lucide-react";


function LearningRecommendations({
    recommendations = []
}) {

    return (

        <section className="dashboard-section">

            <div className="section-title">

                <div>

                    <p className="eyebrow">
                        CAREER DEVELOPMENT
                    </p>

                    <h2>
                        Learning Recommendations
                    </h2>

                </div>

            </div>


            {recommendations.length === 0 ? (

                <div className="empty-state">

                    <BookOpen size={32} />

                    <p>
                        No learning recommendations
                        available.
                    </p>

                </div>

            ) : (

                <div className="learning-grid">

                    {recommendations.map(
                        (item, index) => (

                            <div
                                className="learning-card"
                                key={index}
                            >

                                <div className="learning-icon">

                                    <BookOpen
                                        size={21}
                                    />

                                </div>


                                <div className="learning-content">

                                    <h3>
                                        {item.skill}
                                    </h3>

                                    <p>
                                        {
                                            item.reason ||
                                            "Recommended for improving your job match."
                                        }
                                    </p>

                                </div>


                                <ArrowRight
                                    size={19}
                                />

                            </div>

                        )
                    )}

                </div>

            )}

        </section>
    );
}


export default LearningRecommendations;