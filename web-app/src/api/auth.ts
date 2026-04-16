import { apiClient } from './client';
import type { UserResponse, LoginResponse, VerifyTokenResponse } from './types';

export function register(email: string, fullName: string, password: string): Promise<UserResponse> {
  return apiClient.post<UserResponse>('auth', '/auth/register', {
    email,
    full_name: fullName,
    password,
  });
}

export function login(email: string, password: string): Promise<LoginResponse> {
  return apiClient.post<LoginResponse>('auth', '/auth/login', { email, password });
}

export function refresh(refreshToken: string): Promise<LoginResponse> {
  return apiClient.post<LoginResponse>('auth', '/auth/refresh', { refresh_token: refreshToken });
}

export function logout(refreshToken: string): Promise<void> {
  return apiClient.post<void>('auth', '/auth/logout', { refresh_token: refreshToken });
}

export function getMe(): Promise<UserResponse> {
  return apiClient.get<UserResponse>('auth', '/auth/me');
}

export function verifyToken(): Promise<VerifyTokenResponse> {
  return apiClient.get<VerifyTokenResponse>('auth', '/auth/verify');
}
