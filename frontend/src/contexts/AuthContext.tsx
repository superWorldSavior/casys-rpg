import React, { createContext, useContext, useState, useEffect } from 'react';
import { GoogleOAuthProvider, CredentialResponse } from '@react-oauth/google';
import { jwtDecode } from 'jwt-decode';

interface User {
  email: string;
  name: string;
  picture: string;
  sub: string;
}

interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: User | null;
  login: (response: CredentialResponse) => void;
  logout: () => void;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Verify Google Client ID
    if (!import.meta.env.VITE_GOOGLE_CLIENT_ID) {
      setError('Google Client ID is not configured');
      return;
    }

    // Check for existing session
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser) as User;
        setUser(parsedUser);
        setIsAuthenticated(true);
      } catch (err) {
        console.error('Error parsing stored user:', err);
        localStorage.removeItem('user');
      }
    }
  }, []);

  const login = (response: CredentialResponse) => {
    try {
      if (!response.credential) {
        throw new Error('No credentials received');
      }

      const decoded = jwtDecode(response.credential) as User;
      setUser(decoded);
      setIsAuthenticated(true);
      localStorage.setItem('user', JSON.stringify(decoded));
      setError(null);
    } catch (err) {
      console.error('Login error:', err);
      setError(err instanceof Error ? err.message : 'An error occurred during login');
      setIsAuthenticated(false);
      setUser(null);
    }
  };

  const logout = () => {
    setUser(null);
    setIsAuthenticated(false);
    setError(null);
    localStorage.removeItem('user');
  };

  useEffect(() => {
    // Set loading to false after initial auth check
    setIsLoading(false);
  }, [isAuthenticated]);

  return (
    <GoogleOAuthProvider 
      clientId={import.meta.env.VITE_GOOGLE_CLIENT_ID || ''}
      onScriptLoadError={() => setError('Failed to load Google Sign-In')}
      onScriptLoadSuccess={() => setError(null)}
      auto_select="true"
    >
      <AuthContext.Provider value={{ isAuthenticated, isLoading, user, login, logout, error }}>
        {children}
      </AuthContext.Provider>
    </GoogleOAuthProvider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
