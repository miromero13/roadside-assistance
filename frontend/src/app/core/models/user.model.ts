import { UsuarioAuth } from './auth.model';

export interface PerfilActualizarRequest {
  nombre?: string;
  apellido?: string;
  telefono?: string;
  foto_url?: string;
  password_actual?: string;
  password_nueva?: string;
}

export type PerfilUsuario = UsuarioAuth;
