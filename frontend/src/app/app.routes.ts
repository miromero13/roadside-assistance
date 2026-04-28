import { Routes } from '@angular/router';

import { AppShellComponent } from './core/layouts/app-shell.component';
import {
  authenticatedGuard,
  publicOnlyGuard,
  roleGuard,
} from './core/guards/auth.guards';

export const routes: Routes = [
  {
    path: 'auth/login',
    loadComponent: () =>
      import('./features/auth/pages/login-page.component').then(
        (m) => m.LoginPageComponent,
      ),
    canActivate: [publicOnlyGuard],
  },
  {
    path: 'auth/register',
    loadComponent: () =>
      import('./features/auth/pages/register-page.component').then(
        (m) => m.RegisterPageComponent,
      ),
    canActivate: [publicOnlyGuard],
  },
  {
    path: 'app',
    component: AppShellComponent,
    canActivate: [authenticatedGuard],
    children: [
      {
        path: '',
        pathMatch: 'full',
        redirectTo: 'perfil',
      },
      {
        path: 'perfil',
        loadComponent: () =>
          import('./features/profile/pages/profile-page.component').then(
            (m) => m.ProfilePageComponent,
          ),
      },
      {
        path: 'conductor',
        canActivate: [roleGuard(['conductor'])],
        children: [
          {
            path: '',
            loadComponent: () =>
              import('./features/home/pages/conductor-home-page.component').then(
                (m) => m.ConductorHomePageComponent,
              ),
          },
          {
            path: 'vehiculos',
            loadComponent: () =>
              import('./features/conductor/pages/conductor-vehiculos-page.component').then(
                (m) => m.ConductorVehiculosPageComponent,
              ),
          },
          {
            path: 'averias',
            loadComponent: () =>
              import('./features/conductor/pages/conductor-averias-page.component').then(
                (m) => m.ConductorAveriasPageComponent,
              ),
          },
          {
            path: 'ordenes',
            loadComponent: () =>
              import('./features/conductor/pages/conductor-ordenes-page.component').then(
                (m) => m.ConductorOrdenesPageComponent,
              ),
          },
          {
            path: 'ordenes/:ordenId',
            loadComponent: () =>
              import(
                './features/conductor/pages/conductor-orden-detalle-page.component'
              ).then((m) => m.ConductorOrdenDetallePageComponent),
          },
          {
            path: 'notificaciones',
            loadComponent: () =>
              import(
                './features/conductor/pages/conductor-notificaciones-page.component'
              ).then((m) => m.ConductorNotificacionesPageComponent),
          },
        ],
      },
      {
        path: 'taller',
        canActivate: [roleGuard(['taller'])],
        children: [
          {
            path: '',
            loadComponent: () =>
              import('./features/home/pages/taller-home-page.component').then(
                (m) => m.TallerHomePageComponent,
              ),
          },
          {
            path: 'ordenes',
            loadComponent: () =>
              import('./features/taller/pages/taller-ordenes-page.component').then(
                (m) => m.TallerOrdenesPageComponent,
              ),
          },
          {
            path: 'ordenes/:ordenId',
            loadComponent: () =>
              import('./features/taller/pages/taller-orden-detalle-page.component').then(
                (m) => m.TallerOrdenDetallePageComponent,
              ),
          },
          {
            path: 'comisiones',
            loadComponent: () =>
              import('./features/taller/pages/taller-comisiones-page.component').then(
                (m) => m.TallerComisionesPageComponent,
              ),
          },
          {
            path: 'perfil',
            loadComponent: () =>
              import('./features/taller/pages/taller-perfil-page.component').then(
                (m) => m.TallerPerfilPageComponent,
              ),
          },
          {
            path: 'servicios',
            loadComponent: () =>
              import('./features/taller/pages/taller-servicios-page.component').then(
                (m) => m.TallerServiciosPageComponent,
              ),
          },
          {
            path: 'disponibilidad',
            loadComponent: () =>
              import(
                './features/taller/pages/taller-disponibilidad-page.component'
              ).then((m) => m.TallerDisponibilidadPageComponent),
          },
          {
            path: 'notificaciones',
            loadComponent: () =>
              import(
                './features/taller/pages/taller-notificaciones-page.component'
              ).then((m) => m.TallerNotificacionesPageComponent),
          },
        ],
      },
      {
        path: 'mecanico',
        canActivate: [roleGuard(['mecanico'])],
        children: [
          {
            path: '',
            loadComponent: () =>
              import('./features/home/pages/mecanico-home-page.component').then(
                (m) => m.MecanicoHomePageComponent,
              ),
          },
          {
            path: 'asignaciones',
            loadComponent: () =>
              import(
                './features/mecanico/pages/mecanico-asignaciones-page.component'
              ).then((m) => m.MecanicoAsignacionesPageComponent),
          },
          {
            path: 'asignaciones/:asignacionId',
            loadComponent: () =>
              import(
                './features/mecanico/pages/mecanico-asignacion-detalle-page.component'
              ).then((m) => m.MecanicoAsignacionDetallePageComponent),
          },
        ],
      },
      {
        path: 'admin',
        canActivate: [roleGuard(['admin'])],
        children: [
          {
            path: '',
            loadComponent: () =>
              import('./features/home/pages/admin-home-page.component').then(
                (m) => m.AdminHomePageComponent,
              ),
          },
          {
            path: 'usuarios',
            loadComponent: () =>
              import('./features/admin/pages/admin-usuarios-page.component').then(
                (m) => m.AdminUsuariosPageComponent,
              ),
          },
          {
            path: 'operaciones',
            loadComponent: () =>
              import('./features/admin/pages/admin-operaciones-page.component').then(
                (m) => m.AdminOperacionesPageComponent,
              ),
          },
          {
            path: 'operaciones/:tallerId',
            loadComponent: () =>
              import('./features/admin/pages/admin-operaciones-detalle-page.component').then(
                (m) => m.AdminOperacionesDetallePageComponent,
              ),
          },
          {
            path: 'catalogo',
            loadComponent: () =>
              import('./features/admin/pages/admin-catalogo-page.component').then(
                (m) => m.AdminCatalogoPageComponent,
              ),
          },
          {
            path: 'ordenes',
            loadComponent: () =>
              import('./features/admin/pages/admin-ordenes-page.component').then(
                (m) => m.AdminOrdenesPageComponent,
              ),
          },
          {
            path: 'finanzas',
            loadComponent: () =>
              import('./features/admin/pages/admin-finanzas-page.component').then(
                (m) => m.AdminFinanzasPageComponent,
              ),
          },
          {
            path: 'metricas',
            loadComponent: () =>
              import('./features/admin/pages/admin-metricas-page.component').then(
                (m) => m.AdminMetricasPageComponent,
              ),
          },
        ],
      },
    ],
  },
  {
    path: '',
    pathMatch: 'full',
    redirectTo: 'app',
  },
  {
    path: '**',
    redirectTo: 'app',
  },
];
