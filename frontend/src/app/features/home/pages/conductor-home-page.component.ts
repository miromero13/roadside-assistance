import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';

import { ConductorApiService } from '../../../core/services/conductor-api.service';

@Component({
  selector: 'app-conductor-home-page',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <section class="space-y-5">
      <h1 class="text-2xl font-semibold">Inicio Conductor</h1>

      <div class="grid gap-3 sm:grid-cols-4">
        <article class="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <p class="text-xs uppercase tracking-wide text-slate-500">Vehículos</p>
          <p class="mt-2 text-2xl font-semibold">{{ vehiculosCount() }}</p>
        </article>
        <article class="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <p class="text-xs uppercase tracking-wide text-slate-500">Averías</p>
          <p class="mt-2 text-2xl font-semibold">{{ averiasCount() }}</p>
        </article>
        <article class="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <p class="text-xs uppercase tracking-wide text-slate-500">Órdenes</p>
          <p class="mt-2 text-2xl font-semibold">{{ ordenesCount() }}</p>
        </article>
        <article class="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <p class="text-xs uppercase tracking-wide text-slate-500">No leídas</p>
          <p class="mt-2 text-2xl font-semibold">{{ noLeidasCount() }}</p>
        </article>
      </div>

      <div class="flex flex-wrap gap-2">
        <a routerLink="/app/conductor/vehiculos" class="rounded-lg bg-slate-900 px-4 py-2 text-sm text-white">Gestionar vehículos</a>
        <a routerLink="/app/conductor/averias" class="rounded-lg border border-slate-300 px-4 py-2 text-sm">Gestionar averías</a>
        <a routerLink="/app/conductor/ordenes" class="rounded-lg border border-slate-300 px-4 py-2 text-sm">Ver órdenes</a>
        <a routerLink="/app/conductor/notificaciones" class="rounded-lg border border-slate-300 px-4 py-2 text-sm">Notificaciones</a>
      </div>

      @if (errorMessage()) {
        <p class="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">{{ errorMessage() }}</p>
      }
    </section>
  `,
})
export class ConductorHomePageComponent {
  private readonly api = inject(ConductorApiService);

  protected readonly vehiculosCount = signal(0);
  protected readonly averiasCount = signal(0);
  protected readonly ordenesCount = signal(0);
  protected readonly noLeidasCount = signal(0);
  protected readonly errorMessage = signal('');

  constructor() {
    void this.loadSummary();
  }

  private async loadSummary(): Promise<void> {
    try {
      const [vehiculos, averias, ordenes, notificaciones] = await Promise.all([
        firstValueFrom(this.api.listVehiculos()),
        firstValueFrom(this.api.listAverias()),
        firstValueFrom(this.api.listOrdenes()),
        firstValueFrom(this.api.listNotificaciones(true)),
      ]);

      this.vehiculosCount.set(vehiculos.data?.length ?? 0);
      this.averiasCount.set(averias.data?.length ?? 0);
      this.ordenesCount.set(ordenes.data?.length ?? 0);
      this.noLeidasCount.set(notificaciones.data?.length ?? 0);
    } catch {
      this.errorMessage.set('No se pudo cargar el resumen del conductor.');
    }
  }
}
