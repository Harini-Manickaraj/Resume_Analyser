import React from "react";

import {
    BriefcaseBusiness,
    ArrowUpRight
} from "lucide-react";


function JobRecommendations({
    jobs = []
}) {

    return (

        <section className="dashboard-section">

            <div className="section-title">

                <div>

                    <p className="eyebrow">
                        JOB MATCHING
                    </p>

                    <h2>
                        Recommended Jobs
                    </h2>

                </div>

                <span className="result-count">
                    {jobs.length} matches
                </span>

            </div>


            {jobs.length === 0 ? (

                <div className="empty-state">

                    <BriefcaseBusiness
                        size={32}
                    />

                    <p>
                        No job recommendations
                        available yet.
                    </p>

                </div>

            ) : (

                <div className="job-list">

                    {jobs.map(
                        (job, index) => {

                            const score =
                                Number(
                                    job.match_percentage ||
                                    0
                                );

                            return (

                                <div
                                    className="job-card"
                                    key={
                                        job.job_id ||
                                        index
                                    }
                                >

                                    <div className="job-rank">
                                        #{index + 1}
                                    </div>


                                    <div className="job-icon">
                                        <BriefcaseBusiness
                                            size={20}
                                        />
                                    </div>


                                    <div className="job-info">

                                        <h3>
                                            {
                                                job.job_title ||
                                                "Unknown Position"
                                            }
                                        </h3>

                                        <span>
                                            {
                                                job.job_id ||
                                                "JOB"
                                            }
                                        </span>


                                        <div className="progress-bar">

                                            <div
                                                className="progress-fill"
                                                style={{
                                                    width:
                                                        `${Math.min(
                                                            score,
                                                            100
                                                        )}%`
                                                }}
                                            />

                                        </div>

                                    </div>


                                    <div className="job-score">

                                        <strong>
                                            {score.toFixed(1)}%
                                        </strong>

                                        <span>
                                            {
                                                job.classification ||
                                                "Match"
                                            }
                                        </span>

                                    </div>


                                    <ArrowUpRight
                                        size={20}
                                        className="job-arrow"
                                    />

                                </div>

                            );
                        }
                    )}

                </div>
            )}

        </section>
    );
}


export default JobRecommendations;