import { Injectable, inject } from '@angular/core';

import { ApiService } from './api.service';
import {
  AuthResponse,
  LoginRequest,
  RegisterConductorRequest,
} from '../models/auth.model';

@Injectable({ providedIn: 'root' })
export class AuthApiService {
  private readonly api = inject(ApiService);

  login(payload: LoginRequest) {
    return this.api.post<AuthResponse>('/auth/login', payload);
  }

  registerConductor(payload: RegisterConductorRequest) {
    return this.api.post<AuthResponse>('/auth/register', payload);
  }

  logout() {
    return this.api.post<{ message: string }>('/auth/logout', {});
  }
}
