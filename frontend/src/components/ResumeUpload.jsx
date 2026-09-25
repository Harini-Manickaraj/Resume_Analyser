import React, {
    useRef,
    useState
} from "react";

import {
    Upload,
    FileText,
    X,
    Loader2
} from "lucide-react";


function ResumeUpload({
    onAnalyze,
    loading
}) {

    const fileInputRef = useRef(null);

    const [file, setFile] = useState(null);

    const [dragging, setDragging] =
        useState(false);


    // ========================================================
    // FILE VALIDATION
    // ========================================================

    const validateFile = (
        selectedFile
    ) => {

        if (!selectedFile) {
            return false;
        }

        const name =
            selectedFile.name.toLowerCase();

        return (
            name.endsWith(".pdf") ||
            name.endsWith(".docx")
        );
    };


    // ========================================================
    // HANDLE FILE
    // ========================================================

    const handleFile = (
        selectedFile
    ) => {

        if (!selectedFile) {
            return;
        }

        if (!validateFile(selectedFile)) {

            alert(
                "Please upload a PDF or DOCX resume."
            );

            return;
        }

        setFile(selectedFile);
    };


    // ========================================================
    // INPUT
    // ========================================================

    const handleInputChange = (
        event
    ) => {

        const selectedFile =
            event.target.files?.[0];

        handleFile(selectedFile);
    };


    // ========================================================
    // DRAG EVENTS
    // ========================================================

    const handleDragOver = (
        event
    ) => {

        event.preventDefault();

        setDragging(true);
    };


    const handleDragLeave = (
        event
    ) => {

        event.preventDefault();

        setDragging(false);
    };


    const handleDrop = (
        event
    ) => {

        event.preventDefault();

        setDragging(false);

        const droppedFile =
            event.dataTransfer.files?.[0];

        handleFile(droppedFile);
    };


    // ========================================================
    // REMOVE FILE
    // ========================================================

    const removeFile = () => {

        setFile(null);

        if (fileInputRef.current) {

            fileInputRef.current.value =
                "";
        }
    };


    // ========================================================
    // ANALYZE
    // ========================================================

    const handleAnalyze = async () => {

        if (!file) {

            alert(
                "Please select a resume first."
            );

            return;
        }

        await onAnalyze(file);
    };


    return (

        <section className="upload-section">

            <div className="section-heading">

                <div>

                    <p className="eyebrow">
                        RESUME ANALYSIS
                    </p>

                    <h1>
                        Upload your resume
                    </h1>

                    <p>
                        Let AI analyze your resume,
                        identify your skills and find
                        suitable job opportunities.
                    </p>

                </div>

            </div>


            <div
                className={
                    `upload-box ${
                        dragging
                            ? "dragging"
                            : ""
                    }`
                }

                onDragOver={
                    handleDragOver
                }

                onDragLeave={
                    handleDragLeave
                }

                onDrop={
                    handleDrop
                }

                onClick={() =>
                    fileInputRef.current?.click()
                }
            >

                <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.docx"
                    onChange={
                        handleInputChange
                    }
                    hidden
                />


                {!file ? (

                    <>

                        <div className="upload-icon">
                            <Upload size={32} />
                        </div>

                        <h3>
                            Drop your resume here
                        </h3>

                        <p>
                            or click to browse
                        </p>

                        <span className="file-types">
                            PDF or DOCX
                        </span>

                    </>

                ) : (

                    <div
                        className="selected-file"
                        onClick={(event) =>
                            event.stopPropagation()
                        }
                    >

                        <div className="file-icon">
                            <FileText size={28} />
                        </div>

                        <div className="file-details">

                            <strong>
                                {file.name}
                            </strong>

                            <span>
                                {(
                                    file.size / 1024
                                ).toFixed(1)} KB
                            </span>

                        </div>


                        <button
                            className="remove-file"
                            onClick={
                                removeFile
                            }
                        >
                            <X size={18} />
                        </button>

                    </div>

                )}

            </div>


            <button
                className="analyze-button"
                onClick={handleAnalyze}
                disabled={
                    !file || loading
                }
            >

                {loading ? (

                    <>
                        <Loader2
                            size={20}
                            className="spin"
                        />

                        Analyzing Resume...
                    </>

                ) : (

                    <>
                        <SparklesIcon />

                        Analyze Resume
                    </>

                )}

            </button>

        </section>
    );
}


// Small reusable icon
function SparklesIcon() {

    return (
        <span>
            ✦
        </span>
    );
}


export default ResumeUpload;