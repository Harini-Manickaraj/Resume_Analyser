import React from "react";

import {
    Brain,
    Sparkles
} from "lucide-react";


function Navbar() {

    return (

        <nav className="navbar">

            <div className="navbar-brand">

                <div className="brand-icon">
                    <Brain size={24} />
                </div>

                <div>

                    <h2>
                        ResumeIQ
                    </h2>

                    <span>
                        AI Resume Intelligence
                    </span>

                </div>

            </div>


            <div className="navbar-status">

                <Sparkles size={16} />

                <span>
                    AI Powered
                </span>

            </div>

        </nav>
    );
}


export default Navbar;