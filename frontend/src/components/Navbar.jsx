import React from "react";
import { Brain, Sparkles, FileText, BarChart2 } from "lucide-react";

function Navbar() {
    return (
        <nav className="navbar">
            <div className="navbar-brand">
                <div className="brand-icon">
                    <Brain size={20} />
                </div>
                <div className="navbar-brand-text">
                    <h2>ResumeIQ</h2>
                    <span>AI Resume Intelligence</span>
                </div>
            </div>

            <div className="navbar-right">
                <div className="navbar-badge">
                    <Sparkles size={13} />
                    <span>AI Powered</span>
                </div>
            </div>
        </nav>
    );
}

export default Navbar;
