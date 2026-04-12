// Central configuration for API endpoints.
// Override via .env file: EXPO_PUBLIC_AUTH_URL and EXPO_PUBLIC_API_URL

export const AUTH_BASE_URL =
  process.env.EXPO_PUBLIC_AUTH_URL || 'http://localhost:8001';

export const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';
