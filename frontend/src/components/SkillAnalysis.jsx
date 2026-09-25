import React from "react";
import { CheckCircle2, AlertTriangle } from "lucide-react";

function SkillAnalysis({ skills }) {
    if (!skills) return null;

    const matched = skills.matched || [];
    const missing = skills.missing || [];

    return (
        <section className="dashboard-section">
            <div className="section-title">
                <div>
                    <p className="eyebrow">SKILL INTELLIGENCE</p>
                    <h2>Skill Analysis</h2>
                </div>
            </div>

            <div className="skills-grid">
                {/* Matched skills */}
                <div className="skills-panel matched-panel">
                    <div className="skills-header">
                        <CheckCircle2 size={20} />
                        <div className="skills-header-text">
                            <h3>Matched Skills</h3>
                            <span>Skills found in your resume</span>
                        </div>
                        <span className="skill-count-badge">{matched.length}</span>
                    </div>

                    <div className="skill-tags">
                        {matched.length > 0 ? (
                            matched.map((skill, index) => (
                                <span className="skill-tag matched" key={index}>
                                    {skill}
                                </span>
                            ))
                        ) : (
                            <p className="no-skills">No matched skills detected.</p>
                        )}
                    </div>
                </div>

                {/* Missing skills */}
                <div className="skills-panel missing-panel">
                    <div className="skills-header">
                        <AlertTriangle size={20} />
                        <div className="skills-header-text">
                            <h3>Missing Skills</h3>
                            <span>Skills to add to your profile</span>
                        </div>
                        <span className="skill-count-badge">{missing.length}</span>
                    </div>

                    <div className="skill-tags">
                        {missing.length > 0 ? (
                            missing.map((skill, index) => (
                                <span className="skill-tag missing" key={index}>
                                    {skill}
                                </span>
                            ))
                        ) : (
                            <p className="no-skills">No major skill gaps found.</p>
                        )}
                    </div>
                </div>
            </div>
        </section>
    );
}

export default SkillAnalysis;
