import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, BehaviorSubject, tap } from 'rxjs';
import { TokenResponse, User } from './models';

export const API_URL = 'http://127.0.0.1:8000';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  private readonly currentUserSubject = new BehaviorSubject<User | null>(null);
  readonly currentUser$ = this.currentUserSubject.asObservable();
  login(username: string, password: string): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${API_URL}/auth/login`, { username, password }).pipe(
      tap(tokens => {
        localStorage.setItem('access_token', tokens.access_token);
        localStorage.setItem('refresh_token', tokens.refresh_token);
      }),
    );
  }
  register(username: string, email: string, password: string) {
    return this.http.post<User>(`${API_URL}/auth/register`, { username, email, password });
  }
  me() { return this.http.get<User>(`${API_URL}/auth/me`); }
  loadCurrentUser() {
    return this.me().pipe(tap(user => this.currentUserSubject.next(user)));
  }
  currentUser() { return this.currentUserSubject.value; }
  setCurrentUser(user: User) { this.currentUserSubject.next(user); }
  isAdmin() { return this.currentUser()?.role === 'admin'; }
  logout() {
    const token = localStorage.getItem('access_token');
    if (token) {
      this.http.post(`${API_URL}/auth/logout`, {}).subscribe({ complete: () => this.clearSession(), error: () => this.clearSession() });
    } else {
      this.clearSession();
    }
    this.router.navigate(['/login']);
  }
  private clearSession() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.currentUserSubject.next(null);
  }
  isAuthenticated() { return Boolean(localStorage.getItem('access_token')); }
}
