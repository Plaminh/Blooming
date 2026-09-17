import { writable, get } from 'svelte/store';
import { browser } from '$app/environment';
import { goto } from '$app/navigation';
import { PUBLIC_API_BASE_URL } from '$env/static/public';

const TOKEN_KEY = 'blooming_access_token';

interface User {
  id: string;
  email: string;
  display_name: string;
  is_verified: boolean;
  // add other user fields as needed
}

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  isInitialized: boolean;
}

const getInitialState = (): AuthState => {
  let token = null;
  if (browser) {
    token = localStorage.getItem(TOKEN_KEY);
  }
  return {
    token,
    user: null,
    isAuthenticated: !!token,
    isInitialized: false,
  };
};

const createAuthStore = () => {
  const { subscribe, set, update } = writable<AuthState>(getInitialState());

  return {
    subscribe,
    setToken: (newToken: string) => {
      if (browser) {
        localStorage.setItem(TOKEN_KEY, newToken);
      }
      update(state => ({
        ...state,
        token: newToken,
        isAuthenticated: true,
      }));
    },
    clearAuth: () => {
      if (browser) {
        localStorage.removeItem(TOKEN_KEY);
      }
      set({
        token: null,
        user: null,
        isAuthenticated: false,
        isInitialized: true,
      });
      if (browser) {
        goto('/auth');
      }
    },
    initialize: async () => {
      const state = get({subscribe});
      if (state.isInitialized) return;
      
      if (state.token) {
        try {
          const response = await fetch(`${PUBLIC_API_BASE_URL}/api/v1/me`, {
            headers: {
              'Authorization': `Bearer ${state.token}`
            }
          });
          
          if (!response.ok) {
            throw new Error('Failed to fetch user');
          }
          
          const user = await response.json();
          update(s => ({
            ...s,
            user,
            isAuthenticated: true,
            isInitialized: true,
          }));
        } catch (error) {
          console.error("Failed to fetch user during auth initialization", error);
          if (browser) {
            localStorage.removeItem(TOKEN_KEY);
          }
          update(s => ({
            ...s,
            token: null,
            user: null,
            isAuthenticated: false,
            isInitialized: true,
          }));
        }
      } else {
        update(s => ({ ...s, isInitialized: true }));
      }
    }
  };
};

export const authStore = createAuthStore();
