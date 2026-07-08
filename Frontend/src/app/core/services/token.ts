import { Injectable } from '@angular/core';
import { Session } from '../models/auth.model';

@Injectable({
  providedIn: 'root',
})
export class TokenService {

  private readonly SESSION_KEY = 'ecclesia_session';

  private isBrowser(): boolean {
    return typeof window !== 'undefined';
  }

  getSession(): any {

    if (!this.isBrowser()) {
      return null;
    }

    const data = localStorage.getItem(
      this.SESSION_KEY
    );

    if (!data) {
      return null;
    }

    return JSON.parse(data);
  }

  saveSession(session: any): void {

    if (!this.isBrowser()) {
      return;
    }

    localStorage.setItem(
      this.SESSION_KEY,
      JSON.stringify(session)
    );
  }

  clearSession(): void {

    if (!this.isBrowser()) {
      return;
    }

    localStorage.removeItem(
      this.SESSION_KEY
    );
  }

  getAccessToken(): string | null {
    return this.getSession()?.access_token ?? null;
  }

  getRefreshToken(): string | null {
    return this.getSession()?.refresh_token ?? null;
  }

  isLoggedIn(): boolean {
    return !!this.getAccessToken();
  }

  getUserData(): Session | null {
  return this.getSession();
  }
}