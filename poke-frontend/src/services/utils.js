const API_URL = "http://localhost:8000/api/pokemon/";

export const getAuthHeaders = () => {
  const token = localStorage.getItem("token");
  return token ? { 
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}` 
  } : {};
};

const handleResponse = async (response) => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || errorData.detail || `Error: ${response.status}`);
  }
  return response.json();
};

export const apiRequest = async (endpoint, options = {}) => {
  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      headers: getAuthHeaders(),
      ...options,
    });
    return await handleResponse(response);
  } catch (error) {
    console.error(`API Error (${endpoint}):`, error);
    throw error;
  }
};