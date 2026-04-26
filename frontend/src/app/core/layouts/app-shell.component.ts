import { CommonModule } from '@angular/common';
import { Component, computed, inject } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

import { SessionService } from '../services/session.service';

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive, RouterOutlet],
  template: `
    <div class="min-h-screen bg-slate-100 text-slate-900">
      <header class="border-b border-slate-200 bg-white/90 backdrop-blur">
        <div class="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:px-6">
          <div>
            <p class="text-lg font-semibold">ACI Web</p>
            <p class="text-xs text-slate-500">Panel operativo</p>
          </div>

          <div class="flex items-center gap-3 text-sm">
            <div class="text-right">
              <p class="font-medium">{{ fullName() }}</p>
              <p class="text-xs uppercase tracking-wide text-slate-500">{{ userRole() }}</p>
            </div>
            <button
              type="button"
              class="rounded-lg border border-slate-300 px-3 py-2 text-sm hover:bg-slate-50"
              (click)="logout()"
            >
              Cerrar sesión
            </button>
          </div>
        </div>
      </header>

      <div class="mx-auto grid max-w-6xl gap-4 px-4 py-4 sm:px-6 md:grid-cols-[220px_1fr]">
        <aside class="rounded-xl border border-slate-200 bg-white p-3">
          <nav class="space-y-1 text-sm">
            <a
              routerLink="/app/perfil"
              routerLinkActive="bg-slate-900 text-white"
              class="block rounded-lg px-3 py-2 hover:bg-slate-100"
            >
              Mi perfil
            </a>

            @if (userRole() === 'conductor') {
              <a
                routerLink="/app/conductor"
                routerLinkActive="bg-slate-900 text-white"
                class="block rounded-lg px-3 py-2 hover:bg-slate-100"
              >
                Dashboard conductor
              </a>
              <a
                routerLink="/app/conductor/vehiculos"
                routerLinkActive="bg-slate-900 text-white"
                class="block rounded-lg px-3 py-2 hover:bg-slate-100"
              >
                Vehículos
              </a>
              <a
                routerLink="/app/conductor/averias"
                routerLinkActive="bg-slate-900 text-white"
                class="block rounded-lg px-3 py-2 hover:bg-slate-100"
              >
                Averías
              </a>
              <a
                routerLink="/app/conductor/ordenes"
                routerLinkActive="bg-slate-900 text-white"
                class="block rounded-lg px-3 py-2 hover:bg-slate-100"
              >
                Órdenes
              </a>
              <a
                routerLink="/app/conductor/notificaciones"
                routerLinkActive="bg-slate-900 text-white"
                class="block rounded-lg px-3 py-2 hover:bg-slate-100"
              >
                Notificaciones
              </a>
            }

            @if (userRole() === 'taller') {
              <a
                routerLink="/app/taller"
                routerLinkActive="bg-slate-900 text-white"
                class="block rounded-lg px-3 py-2 hover:bg-slate-100"
              >
                Dashboard taller
              </a>
              <a
                routerLink="/app/taller/ordenes"
                routerLinkActive="bg-slate-900 text-white"
                class="block rounded-lg px-3 py-2 hover:bg-slate-100"
              >
                Órdenes taller
              </a>
              <a
                routerLink="/app/taller/comisiones"
                routerLinkActive="bg-slate-900 text-white"
                class="block rounded-lg px-3 py-2 hover:bg-slate-100"
              >
                Comisiones
              </a>
              <a
                routerLink="/app/taller/servicios"
                routerLinkActive="bg-slate-900 text-white"
                class="block rounded-lg px-3 py-2 hover:bg-slate-100"
              >
                Servicios
              </a>
              <a
                routerLink="/app/taller/disponibilidad"
                routerLinkActive="bg-slate-900 text-white"
                class="block rounded-lg px-3 py-2 hover:bg-slate-100"
              >
                Disponibilidad
              </a>
              <a
                routerLink="/app/taller/perfil"
                routerLinkActive="bg-slate-900 text-white"
                class="block rounded-lg px-3 py-2 hover:bg-slate-100"
              >
                Perfil taller
              </a>
              <a
                routerLink="/app/taller/notificaciones"
                routerLinkActive="bg-slate-900 text-white"
                class="block rounded-lg px-3 py-2 hover:bg-slate-100"
              >
                Notificaciones
              </a>
            }

            @if (userRole() === 'mecanico') {
              <a
                routerLink="/app/mecanico"
                routerLinkActive="bg-slate-900 text-white"
                class="block rounded-lg px-3 py-2 hover:bg-slate-100"
              >
                Dashboard mecánico
              </a>
              <a
                routerLink="/app/mecanico/asignaciones"
                routerLinkActive="bg-slate-900 text-white"
                class="block rounded-lg px-3 py-2 hover:bg-slate-100"
              >
                Mis asignaciones
              </a>
            }

            @if (userRole() === 'admin') {
              <a
                routerLink="/app/admin"
                routerLinkActive="bg-slate-900 text-white"
                class="block rounded-lg px-3 py-2 hover:bg-slate-100"
              >
                Dashboard admin
              </a>
              <a
                routerLink="/app/admin/usuarios"
                routerLinkActive="bg-slate-900 text-white"
                class="block rounded-lg px-3 py-2 hover:bg-slate-100"
              >
                Usuarios
              </a>
              <a
                routerLink="/app/admin/operaciones"
                routerLinkActive="bg-slate-900 text-white"
                class="block rounded-lg px-3 py-2 hover:bg-slate-100"
              >
                Talleres y mecánicos
              </a>
              <a
                routerLink="/app/admin/catalogo"
                routerLinkActive="bg-slate-900 text-white"
                class="block rounded-lg px-3 py-2 hover:bg-slate-100"
              >
                Catálogo
              </a>
              <a
                routerLink="/app/admin/ordenes"
                routerLinkActive="bg-slate-900 text-white"
                class="block rounded-lg px-3 py-2 hover:bg-slate-100"
              >
                Órdenes
              </a>
              <a
                routerLink="/app/admin/finanzas"
                routerLinkActive="bg-slate-900 text-white"
                class="block rounded-lg px-3 py-2 hover:bg-slate-100"
              >
                Finanzas
              </a>
              <a
                routerLink="/app/admin/metricas"
                routerLinkActive="bg-slate-900 text-white"
                class="block rounded-lg px-3 py-2 hover:bg-slate-100"
              >
                Métricas
              </a>
            }
          </nav>
        </aside>

        <main class="rounded-xl border border-slate-200 bg-white p-4 sm:p-6">
          <router-outlet />
        </main>
      </div>
    </div>
  `,
})
export class AppShellComponent {
  private readonly session = inject(SessionService);

  protected readonly fullName = computed(() => {
    const user = this.session.user();
    return user ? `${user.nombre} ${user.apellido}` : 'Sin sesión';
  });

  protected readonly userRole = computed(() => this.session.user()?.rol ?? '-');

  protected async logout(): Promise<void> {
    await this.session.logout(true);
  }
}
