export type RolUsuario = 'conductor' | 'taller' | 'mecanico' | 'admin';

export interface UsuarioAuth {
  id: string;
  nombre: string;
  apellido: string;
  email: string;
  telefono: string;
  rol: RolUsuario;
  activo: boolean;
  foto_url?: string | null;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterConductorRequest {
  nombre: string;
  apellido: string;
  email: string;
  telefono: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: UsuarioAuth;
}
