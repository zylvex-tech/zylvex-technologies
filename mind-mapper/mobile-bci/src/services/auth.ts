import * as SecureStore from 'expo-secure-store';

const TOKEN_KEY = 'mindmapper_auth_token';
const REFRESH_TOKEN_KEY = 'mindmapper_refresh_token';
const USER_ID_KEY = 'mindmapper_user_id';

export const storeToken = async (token: string): Promise<void> => {
  await SecureStore.setItemAsync(TOKEN_KEY, token);
};

export const getToken = async (): Promise<string | null> => {
  return await SecureStore.getItemAsync(TOKEN_KEY);
};

export const clearToken = async (): Promise<void> => {
  await SecureStore.deleteItemAsync(TOKEN_KEY);
  await SecureStore.deleteItemAsync(REFRESH_TOKEN_KEY);
  await SecureStore.deleteItemAsync(USER_ID_KEY);
};

export const storeRefreshToken = async (refreshToken: string): Promise<void> => {
  await SecureStore.setItemAsync(REFRESH_TOKEN_KEY, refreshToken);
};

export const getRefreshToken = async (): Promise<string | null> => {
  return await SecureStore.getItemAsync(REFRESH_TOKEN_KEY);
};

export const storeUserId = async (userId: string): Promise<void> => {
  await SecureStore.setItemAsync(USER_ID_KEY, userId);
};

export const getUserId = async (): Promise<string | null> => {
  return await SecureStore.getItemAsync(USER_ID_KEY);
};
