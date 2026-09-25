import axios from "axios";


const API_BASE_URL = "http://127.0.0.1:8000/api";


const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        Accept: "application/json"
    }
});


// ============================================================
// HEALTH CHECK
// ============================================================

export const getHealth = async () => {

    const response = await api.get(
        "/health"
    );

    return response.data;
};


// ============================================================
// GET JOBS
// ============================================================

export const getJobs = async () => {

    const response = await api.get(
        "/jobs"
    );

    return response.data;
};


// ============================================================
// GET RESUMES
// ============================================================

export const getResumes = async () => {

    const response = await api.get(
        "/resumes"
    );

    return response.data;
};


// ============================================================
// ANALYZE RESUME
// ============================================================

export const analyzeResume = async (
    file
) => {

    const formData = new FormData();

    formData.append(
        "file",
        file
    );

    const response = await api.post(
        "/resume/analyze",
        formData,
        {
            headers: {
                "Content-Type":
                    "multipart/form-data"
            }
        }
    );

    return response.data;
};


// ============================================================
// UPLOAD RESUME
// ============================================================

export const uploadResume = async (
    file
) => {

    const formData = new FormData();

    formData.append(
        "file",
        file
    );

    const response = await api.post(
        "/resume/upload",
        formData,
        {
            headers: {
                "Content-Type":
                    "multipart/form-data"
            }
        }
    );

    return response.data;
};


export default api;