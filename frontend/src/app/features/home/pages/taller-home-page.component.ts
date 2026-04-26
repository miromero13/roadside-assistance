import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';

import { TallerApiService } from '../../../core/services/taller-api.service';

@Component({
  selector: 'app-taller-home-page',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <section class="space-y-5">
      <h1 class="text-2xl font-semibold">Inicio Taller</h1>

      <div class="grid gap-3 sm:grid-cols-4">
        <article class="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <p class="text-xs uppercase tracking-wide text-slate-500">Pendientes</p>
          <p class="mt-2 text-2xl font-semibold">{{ pendientesCount() }}</p>
        </article>
        <article class="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <p class="text-xs uppercase tracking-wide text-slate-500">Aceptadas</p>
          <p class="mt-2 text-2xl font-semibold">{{ aceptadasCount() }}</p>
        </article>
        <article class="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <p class="text-xs uppercase tracking-wide text-slate-500">En proceso</p>
          <p class="mt-2 text-2xl font-semibold">{{ enProcesoCount() }}</p>
        </article>
        <article class="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <p class="text-xs uppercase tracking-wide text-slate-500">Comisiones</p>
          <p class="mt-2 text-2xl font-semibold">{{ comisionesCount() }}</p>
        </article>
      </div>

      <div class="flex flex-wrap gap-2">
        <a routerLink="/app/taller/ordenes" class="rounded-lg bg-slate-900 px-4 py-2 text-sm text-white">Gestionar órdenes</a>
        <a routerLink="/app/taller/comisiones" class="rounded-lg border border-slate-300 px-4 py-2 text-sm">Comisiones</a>
        <a routerLink="/app/taller/servicios" class="rounded-lg border border-slate-300 px-4 py-2 text-sm">Servicios</a>
        <a routerLink="/app/taller/disponibilidad" class="rounded-lg border border-slate-300 px-4 py-2 text-sm">Disponibilidad</a>
        <a routerLink="/app/taller/perfil" class="rounded-lg border border-slate-300 px-4 py-2 text-sm">Perfil</a>
        <a routerLink="/app/taller/notificaciones" class="rounded-lg border border-slate-300 px-4 py-2 text-sm">Notificaciones</a>
      </div>

      @if (errorMessage()) {
        <p class="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">{{ errorMessage() }}</p>
      }
    </section>
  `,
})
export class TallerHomePageComponent {
  private readonly api = inject(TallerApiService);

  protected readonly pendientesCount = signal(0);
  protected readonly aceptadasCount = signal(0);
  protected readonly enProcesoCount = signal(0);
  protected readonly comisionesCount = signal(0);
  protected readonly errorMessage = signal('');

  constructor() {
    void this.loadSummary();
  }

  private async loadSummary(): Promise<void> {
    try {
      const [pendientes, aceptadas, enProceso, comisiones] = await Promise.all([
        firstValueFrom(this.api.listOrdenes('pendiente_respuesta')),
        firstValueFrom(this.api.listOrdenes('aceptada')),
        firstValueFrom(this.api.listOrdenes('en_proceso')),
        firstValueFrom(this.api.listComisionesMias()),
      ]);

      this.pendientesCount.set(pendientes.data?.length ?? 0);
      this.aceptadasCount.set(aceptadas.data?.length ?? 0);
      this.enProcesoCount.set(enProceso.data?.length ?? 0);
      this.comisionesCount.set(comisiones.data?.length ?? 0);
    } catch {
      this.errorMessage.set('No se pudo cargar el resumen del taller.');
    }
  }
}
