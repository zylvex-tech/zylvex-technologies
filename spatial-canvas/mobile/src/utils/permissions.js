// Permissions utility for camera and location
import * as Location from 'expo-location';
import * as Camera from 'expo-camera';

export const requestCameraPermission = async () => {
  const { status } = await Camera.requestCameraPermissionsAsync();
  return { granted: status === 'granted' };
};

export const requestLocationPermission = async () => {
  const { status } = await Location.requestForegroundPermissionsAsync();
  return { granted: status === 'granted' };
};

export const getCurrentLocation = async () => {
  const location = await Location.getCurrentPositionAsync({});
  return {
    latitude: location.coords.latitude,
    longitude: location.coords.longitude,
    altitude: location.coords.altitude || 0,
  };
};
