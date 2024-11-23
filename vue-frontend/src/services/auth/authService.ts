import type { User } from '@/types/auth';

export interface AuthResponse {
  user: User;
  token: string;
}

export class AuthService {
  private static instance: AuthService;
  private readonly API_URL = import.meta.env.VITE_API_URL || '';

  private constructor() {}

  public static getInstance(): AuthService {
    if (!AuthService.instance) {
      AuthService.instance = new AuthService();
    }
    return AuthService.instance;
  }

  async login(email: string, password: string): Promise<AuthResponse> {
    try {
      const response = await fetch(`${this.API_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        throw new Error('Échec de la connexion');
      }

      return await response.json();
    } catch (error) {
      console.error('Erreur lors de la connexion:', error);
      throw error;
    }
  }

  async logout(): Promise<void> {
    try {
      const response = await fetch(`${this.API_URL}/auth/logout`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Échec de la déconnexion');
      }
    } catch (error) {
      console.error('Erreur lors de la déconnexion:', error);
      throw error;
    }
  }

  getStoredToken(): string | null {
    return localStorage.getItem('auth_token');
  }

  setStoredToken(token: string): void {
    localStorage.setItem('auth_token', token);
  }

  removeStoredToken(): void {
    localStorage.removeItem('auth_token');
  }
}

export const authService = AuthService.getInstance();
