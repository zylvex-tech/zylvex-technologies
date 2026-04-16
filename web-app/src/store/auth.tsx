import React, { createContext, useContext, useReducer, useEffect } from 'react';
import type { UserResponse } from '../api/types';
import { setTokens, clearTokens, getStoredRefreshToken } from '../api/client';
import { refresh, getMe } from '../api/auth';

interface AuthState {
  user: UserResponse | null;
  accessToken: string | null;
  refreshToken: string | null;
  isLoading: boolean;
}

type AuthAction =
  | { type: 'SET_TOKENS'; payload: { accessToken: string; refreshToken: string } }
  | { type: 'SET_USER'; payload: UserResponse }
  | { type: 'LOGOUT' }
  | { type: 'SET_LOADING'; payload: boolean };

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'SET_TOKENS':
      return {
        ...state,
        accessToken: action.payload.accessToken,
        refreshToken: action.payload.refreshToken,
      };
    case 'SET_USER':
      return { ...state, user: action.payload };
    case 'LOGOUT':
      return { user: null, accessToken: null, refreshToken: null, isLoading: false };
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    default:
      return state;
  }
}

interface AuthContextValue {
  state: AuthState;
  login: (accessToken: string, refreshToken: string) => Promise<void>;
  logout: () => void;
  setUser: (user: UserResponse) => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, {
    user: null,
    accessToken: null,
    refreshToken: null,
    isLoading: true,
  });

  useEffect(() => {
    const storedRefreshToken = getStoredRefreshToken();
    if (!storedRefreshToken) {
      dispatch({ type: 'SET_LOADING', payload: false });
      return;
    }

    refresh(storedRefreshToken)
      .then(async (tokens) => {
        setTokens(tokens.access_token, tokens.refresh_token);
        dispatch({
          type: 'SET_TOKENS',
          payload: { accessToken: tokens.access_token, refreshToken: tokens.refresh_token },
        });
        const user = await getMe();
        dispatch({ type: 'SET_USER', payload: user });
      })
      .catch(() => {
        clearTokens();
      })
      .finally(() => {
        dispatch({ type: 'SET_LOADING', payload: false });
      });
  }, []);

  const loginFn = async (accessToken: string, refreshToken: string) => {
    setTokens(accessToken, refreshToken);
    dispatch({ type: 'SET_TOKENS', payload: { accessToken, refreshToken } });
    const user = await getMe();
    dispatch({ type: 'SET_USER', payload: user });
  };

  const logoutFn = () => {
    clearTokens();
    dispatch({ type: 'LOGOUT' });
  };

  const setUser = (user: UserResponse) => {
    dispatch({ type: 'SET_USER', payload: user });
  };

  return (
    <AuthContext.Provider value={{ state, login: loginFn, logout: logoutFn, setUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
