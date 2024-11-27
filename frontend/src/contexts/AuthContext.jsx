import React, { createContext, useContext, useState, useEffect, useMemo, useCallback } from "react";
import { Box, CircularProgress } from "@mui/material";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [state, setState] = useState({
    user: null,
    loading: true,
    error: null
  });

  useEffect(() => {
    let mounted = true;

    const initializeAuth = async () => {
      try {
        const storedUser = localStorage.getItem("user");
        if (storedUser && mounted) {
          setState(prev => ({
            ...prev,
            user: JSON.parse(storedUser),
            loading: false
          }));
        } else {
          setState(prev => ({
            ...prev,
            loading: false
          }));
        }
      } catch (err) {
        console.error("Auth initialization error:", err);
        localStorage.removeItem("user");
        if (mounted) {
          setState(prev => ({
            ...prev,
            error: err.message,
            loading: false
          }));
        }
      }
    };

    initializeAuth();
    return () => {
      mounted = false;
    };
  }, []);

  const login = useCallback(async (credentials) => {
    try {
      setState(prev => ({ ...prev, error: null }));
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json",
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify(credentials)
      });

      if (!response.ok) {
        throw new Error("Login failed");
      }

      const userData = await response.json();
      setState(prev => ({ ...prev, user: userData, error: null }));
      localStorage.setItem("user", JSON.stringify(userData));
      return userData;
    } catch (err) {
      setState(prev => ({ ...prev, error: "Invalid credentials" }));
      throw err;
    }
  }, []);

  const logout = useCallback(() => {
    setState(prev => ({ ...prev, user: null, error: null }));
    localStorage.removeItem("user");
  }, []);

  const contextValue = useMemo(() => ({
    user: state.user,
    loading: state.loading,
    error: state.error,
    login,
    logout,
    setError: (error) => setState(prev => ({ ...prev, error })),
  }), [state, login, logout]);

  if (state.loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
        bgcolor="background.default"
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
