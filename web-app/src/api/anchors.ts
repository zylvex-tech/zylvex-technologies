import { apiClient } from './client';
import type { AnchorResponse, AnchorCreate, AnchorsListResponse } from './types';

export function getAnchorsNearby(
  lat: number,
  lng: number,
  radiusKm = 5,
  skip = 0,
  limit = 50,
): Promise<AnchorsListResponse> {
  const params = new URLSearchParams({
    latitude: lat.toString(),
    longitude: lng.toString(),
    radius_km: radiusKm.toString(),
    skip: skip.toString(),
    limit: limit.toString(),
  });
  return apiClient.get<AnchorsListResponse>('spatial', `/api/v1/anchors?${params}`);
}

export function createAnchor(data: AnchorCreate): Promise<AnchorResponse> {
  return apiClient.post<AnchorResponse>('spatial', '/api/v1/anchors', data);
}

export function getMyAnchors(): Promise<AnchorResponse[]> {
  return apiClient.get<AnchorResponse[]>('spatial', '/api/v1/anchors/mine');
}

export function getAnchor(id: string): Promise<AnchorResponse> {
  return apiClient.get<AnchorResponse>('spatial', `/api/v1/anchors/${id}`);
}

export function deleteAnchor(id: string): Promise<void> {
  return apiClient.delete<void>('spatial', `/api/v1/anchors/${id}`);
}
