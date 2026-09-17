import { writable, get } from 'svelte/store';
import { browser } from '$app/environment';
import { goto } from '$app/navigation';
import { api, APIError, setAuthErrorHandler } from '$lib/api';

const TOKEN_KEY = 'blooming_access_token';

interface User {
  id: string;
  email: string;
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

  const store = {
    subscribe,
    updateUser: (userUpdates: Partial<User>) => {
      update(s => s.user ? { ...s, user: { ...s.user, ...userUpdates } } : s);
    },
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
      if (browser && window.location.pathname !== '/auth') {
        // Force full page reload to forcefully clear all active feature stores and context state (goals, garden, today)
        window.location.href = '/auth';
      }
    },
    login: async (email: string, password: string): Promise<boolean> => {
      try {
        const response = await api.post('/auth/login', {
          username: email,
          password: password
        }, { formUrlEncoded: true });
        
        if (response && response.access_token) {
          store.setToken(response.access_token);
          await store.initialize();
          return true;
        }
        return false;
      } catch (error) {
        if (error instanceof APIError) {
          throw error;
        }
        throw new Error('Login failed');
      }
    },
    register: async (email: string, password: string): Promise<boolean> => {
      try {
        const response = await api.post('/auth/register', {
          email,
          password
        });
        
        // Backend returns verification_required=True
        // We should not auto-login.
        if (response) {
          return true;
        }
        return false;
      } catch (error) {
        if (error instanceof APIError) {
          throw error;
        }
        throw new Error('Registration failed');
      }
    },
    initialize: async () => {
      const state = get({subscribe});
      if (state.isInitialized && state.user) return;
      
      if (state.token) {
        try {
          // Use shared api client instead of fetch
          const user = await api.get('/me');
          
          update(s => ({
            ...s,
            user,
            isAuthenticated: true,
            isInitialized: true,
          }));
        } catch (error) {
          console.error("Failed to fetch user during auth initialization", error);
          store.clearAuth();
        }
      } else {
        update(s => ({ ...s, isInitialized: true }));
      }
    }
  };

  // Register the auth error handler to break circular dependency with api.ts
  setAuthErrorHandler(() => {
    store.clearAuth();
  });

  return store;
};

export const authStore = createAuthStore();
