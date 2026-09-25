import React, { useRef, useState } from "react";
import { Upload, FileText, X, Loader2, CheckCircle2, Zap, Shield, Clock } from "lucide-react";

function ResumeUpload({ onAnalyze, loading }) {
    const fileInputRef = useRef(null);
    const [file, setFile]       = useState(null);
    const [dragging, setDragging] = useState(false);
    const [fileError, setFileError] = useState("");

    // ── Validation ──────────────────────────────────────────
    const validateFile = (selectedFile) => {
        if (!selectedFile) return false;
        const name = selectedFile.name.toLowerCase();
        return name.endsWith(".pdf") || name.endsWith(".docx");
    };

    // ── Handle file selection ────────────────────────────────
    const handleFile = (selectedFile) => {
        if (!selectedFile) return;
        setFileError("");
        if (!validateFile(selectedFile)) {
            setFileError("Only PDF or DOCX files are accepted. Please choose a valid resume.");
            return;
        }
        setFile(selectedFile);
    };

    const handleInputChange = (event) => {
        handleFile(event.target.files?.[0]);
    };

    // ── Drag events ──────────────────────────────────────────
    const handleDragOver = (event) => {
        event.preventDefault();
        setDragging(true);
    };

    const handleDragLeave = (event) => {
        event.preventDefault();
        setDragging(false);
    };

    const handleDrop = (event) => {
        event.preventDefault();
        setDragging(false);
        handleFile(event.dataTransfer.files?.[0]);
    };

    // ── Remove file ──────────────────────────────────────────
    const removeFile = () => {
        setFile(null);
        setFileError("");
        if (fileInputRef.current) fileInputRef.current.value = "";
    };

    // ── Analyze ──────────────────────────────────────────────
    const handleAnalyze = async () => {
        if (!file) return;
        await onAnalyze(file);
    };

    const formatSize = (bytes) => {
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    };

    return (
        <section className="upload-section">
            {/* Hero heading */}
            <div className="section-heading">
                <p className="eyebrow">AI RESUME ANALYSIS</p>
                <h1>
                    Upload your resume,{" "}
                    <span className="highlight">get insights instantly</span>
                </h1>
                <p>
                    Our AI analyzes your resume, identifies skill gaps, scores your
                    profile against real job requirements, and recommends the best
                    matching opportunities — all in seconds.
                </p>

                <div className="upload-features">
                    <span className="upload-feature-item">
                        <CheckCircle2 size={14} />
                        Skill extraction
                    </span>
                    <span className="upload-feature-item">
                        <CheckCircle2 size={14} />
                        Semantic matching
                    </span>
                    <span className="upload-feature-item">
                        <CheckCircle2 size={14} />
                        Job recommendations
                    </span>
                    <span className="upload-feature-item">
                        <CheckCircle2 size={14} />
                        Learning roadmap
                    </span>
                </div>
            </div>

            {/* Drop zone */}
            <div
                className={`upload-box${dragging ? " dragging" : ""}`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => !file && fileInputRef.current?.click()}
                role="button"
                tabIndex={0}
                aria-label="Resume upload area"
                onKeyDown={(e) => e.key === "Enter" && !file && fileInputRef.current?.click()}
            >
                <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.docx"
                    onChange={handleInputChange}
                    hidden
                    aria-label="Resume file input"
                />

                {!file ? (
                    <div className="upload-placeholder">
                        <div className="upload-icon">
                            <Upload size={28} />
                        </div>
                        <h3>Drop your resume here</h3>
                        <p className="upload-sub">or click to browse your files</p>
                        <span className="file-types">PDF &nbsp;·&nbsp; DOCX</span>
                    </div>
                ) : (
                    <div
                        className="selected-file"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div className="file-icon">
                            <FileText size={24} />
                        </div>
                        <div className="file-details">
                            <strong>{file.name}</strong>
                            <span>{formatSize(file.size)}</span>
                        </div>
                        <div className="file-valid-badge">
                            <CheckCircle2 size={13} />
                            Ready
                        </div>
                        <button
                            className="remove-file"
                            onClick={removeFile}
                            aria-label="Remove file"
                            title="Remove file"
                        >
                            <X size={16} />
                        </button>
                    </div>
                )}
            </div>

            {/* File validation error */}
            {fileError && (
                <p style={{
                    marginTop: "10px",
                    fontSize: "13px",
                    color: "var(--color-error)",
                    display: "flex",
                    alignItems: "center",
                    gap: "6px"
                }}>
                    ⚠ {fileError}
                </p>
            )}

            {/* Analyze button */}
            <button
                className="analyze-button"
                onClick={handleAnalyze}
                disabled={!file || loading}
                aria-busy={loading}
            >
                {loading ? (
                    <>
                        <Loader2 size={18} className="spin" />
                        Analyzing Resume…
                    </>
                ) : (
                    <>
                        <Zap size={17} />
                        Analyze Resume
                    </>
                )}
            </button>
        </section>
    );
}

export default ResumeUpload;
