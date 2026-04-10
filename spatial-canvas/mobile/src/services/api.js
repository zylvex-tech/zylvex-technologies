// API service for Spatial Canvas
const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

export const anchorAPI = {
  createAnchor: async (data) => {
    const response = await fetch(`${API_URL}/api/v1/anchors`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return response.json();
  },
  
  getNearbyAnchors: async (lat, lng, radius = 0.5) => {
    const response = await fetch(
      `${API_URL}/api/v1/anchors?latitude=${lat}&longitude=${lng}&radius_km=${radius}`
    );
    return response.json();
  },
};
