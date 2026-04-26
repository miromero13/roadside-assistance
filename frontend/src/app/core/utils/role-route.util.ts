import { RolUsuario } from '../models/auth.model';

export function getDefaultRouteForRole(rol: RolUsuario | undefined): string {
  switch (rol) {
    case 'conductor':
      return '/app/conductor';
    case 'taller':
      return '/app/taller';
    case 'mecanico':
      return '/app/mecanico';
    case 'admin':
      return '/app/admin';
    default:
      return '/app/perfil';
  }
}
