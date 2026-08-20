const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

/**
 * Helper to handle fetch responses and error logging
 */
async function handleResponse(response) {
  if (!response.ok) {
    let errorDetail = "API Error";
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errJson.message || JSON.stringify(errJson);
    } catch {
      errorDetail = await response.text();
    }
    throw new Error(errorDetail || `HTTP error! status: ${response.status}`);
  }
  return response.json();
}

/**
 * MediScribe API Client
 */
export const api = {
  baseUrl: API_BASE_URL,

  /**
   * Health check endpoint
   */
  async checkHealth() {
    try {
      const res = await fetch(`${API_BASE_URL}/api/health`);
      return await handleResponse(res);
    } catch (err) {
      console.warn("Backend health check failed:", err.message);
      return { status: "offline", error: err.message };
    }
  },

  /**
   * Step 1: Generate Case Study Summary from transcript
   * @param {Object} params
   * @param {string} params.transcript - Raw dialogue / transcript
   * @param {string} [params.sessionId] - Optional session ID
   * @param {string} [params.patientId] - Optional patient ID
   */
  async generateSummary({ transcript, sessionId, patientId }) {
    const payload = {
      transcript,
      session_id: sessionId || undefined,
      patient_id: patientId || undefined,
    };

    const res = await fetch(`${API_BASE_URL}/api/generate-summary`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
    return await handleResponse(res);
  },

  /**
   * Step 2: Update stored Case Study Summary after doctor review
   * @param {Object} params
   * @param {string} params.sessionId - Session ID
   * @param {Object} params.updatedCaseStudySummary - Updated CaseSheetSummary object
   */
  async updateSummary({ sessionId, updatedCaseStudySummary }) {
    const payload = {
      session_id: sessionId,
      updated_case_study_summary: updatedCaseStudySummary,
    };

    const res = await fetch(`${API_BASE_URL}/api/update-summary`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
    return await handleResponse(res);
  },

  /**
   * Step 3: Generate & Upload PDF for a given session_id
   * @param {string} sessionId - Session ID to generate PDF for
   */
  async generatePdf(sessionId) {
    const res = await fetch(`${API_BASE_URL}/api/generate-pdf`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ session_id: sessionId }),
    });
    return await handleResponse(res);
  },

  /**
   * Step 4: Get consultation details by session_id
   * @param {string} sessionId
   */
  async getConsultation(sessionId) {
    const res = await fetch(`${API_BASE_URL}/api/consultation/${encodeURIComponent(sessionId)}`);
    return await handleResponse(res);
  },

  /**
   * List recent consultations
   * @param {number} [limit=50]
   */
  async listConsultations(limit = 50) {
    const res = await fetch(`${API_BASE_URL}/api/consultations?limit=${limit}`);
    return await handleResponse(res);
  },

  /**
   * Get direct download URL for a consultation PDF
   */
  getDownloadPdfUrl(sessionId) {
    return `${API_BASE_URL}/api/consultation/${encodeURIComponent(sessionId)}/download-pdf`;
  },

  /**
   * Get inline preview URL for a consultation PDF
   */
  getViewPdfUrl(sessionId) {
    return `${API_BASE_URL}/api/consultation/${encodeURIComponent(sessionId)}/pdf`;
  },
};

export default api;
