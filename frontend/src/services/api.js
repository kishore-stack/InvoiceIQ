import axios from 'axios';

const API_BASE_URL =
  import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000,
});
// API service methods
const api = {
  /**
   * Upload invoice file(s)
   * @param {File|FileList} files - Invoice file(s) to upload
   * @param {Function} onUploadProgress - Progress callback
   * @returns {Promise} API response
   */
uploadInvoice: async (files, onUploadProgress) => {
  const formData = new FormData();

  const selectedFile = Array.isArray(files)
    ? files[0]
    : files instanceof FileList
    ? files[0]
    : files;

  formData.append("file", selectedFile);

  return apiClient.post("/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
    onUploadProgress: (progressEvent) => {
      if (onUploadProgress && progressEvent.total) {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        onUploadProgress(percentCompleted);
      }
    },
  });
},

  /**
   * Get invoice by ID
   * @param {string} id - Invoice ID
   * @returns {Promise} API response
   */
  getInvoice: async (id) => {
    return apiClient.get(`/invoice/${id}`);
  },

  /**
   * Get all invoice history
   * @param {Object} params - Query parameters (search, filter, etc.)
   * @returns {Promise} API response
   */
  getHistory: async (params = {}) => {
    return apiClient.get('/history', { params });
  },

  /**
   * Delete invoice by ID
   * @param {string} id - Invoice ID
   * @returns {Promise} API response
   */
  deleteInvoice: async (id) => {
    return apiClient.delete(`/invoice/${id}`);
  },
};

export default api;
