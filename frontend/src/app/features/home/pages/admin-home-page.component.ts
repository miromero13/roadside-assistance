import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';

import { AdminApiService } from '../../../core/services/admin-api.service';
import { getErrorMessage } from '../../../core/utils/http-error.util';

@Component({
  selector: 'app-admin-home-page',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <section class="space-y-5">
      <header>
        <h1 class="text-2xl font-semibold">Dashboard admin</h1>
        <p class="text-sm text-slate-500">Vista rápida de operación, finanzas y métricas.</p>
      </header>

      @if (errorMessage()) {
        <p class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ errorMessage() }}</p>
      }

      <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <article class="rounded-xl border border-slate-200 p-4">
          <p class="text-xs text-slate-500">Usuarios</p>
          <p class="text-2xl font-semibold">{{ usuariosCount() }}</p>
          <a class="mt-2 inline-block text-sm underline" routerLink="/app/admin/usuarios">Gestionar</a>
        </article>
        <article class="rounded-xl border border-slate-200 p-4">
          <p class="text-xs text-slate-500">Órdenes</p>
          <p class="text-2xl font-semibold">{{ ordenesCount() }}</p>
          <a class="mt-2 inline-block text-sm underline" routerLink="/app/admin/ordenes">Supervisar</a>
        </article>
        <article class="rounded-xl border border-slate-200 p-4">
          <p class="text-xs text-slate-500">Pagos</p>
          <p class="text-2xl font-semibold">{{ pagosCount() }}</p>
          <a class="mt-2 inline-block text-sm underline" routerLink="/app/admin/finanzas">Ver finanzas</a>
        </article>
        <article class="rounded-xl border border-slate-200 p-4">
          <p class="text-xs text-slate-500">Métricas</p>
          <p class="text-2xl font-semibold">{{ metricasCount() }}</p>
          <a class="mt-2 inline-block text-sm underline" routerLink="/app/admin/metricas">Ver métricas</a>
        </article>
      </div>
    </section>
  `,
})
export class AdminHomePageComponent {
  private readonly api = inject(AdminApiService);

  protected readonly usuariosCount = signal(0);
  protected readonly ordenesCount = signal(0);
  protected readonly pagosCount = signal(0);
  protected readonly metricasCount = signal(0);
  protected readonly errorMessage = signal('');

  constructor() {
    void this.load();
  }

  private async load(): Promise<void> {
    this.errorMessage.set('');
    try {
      const [usuarios, ordenes, pagos, metricas] = await Promise.all([
        firstValueFrom(this.api.listUsuarios()),
        firstValueFrom(this.api.listOrdenes()),
        firstValueFrom(this.api.listPagos()),
        firstValueFrom(this.api.listMetricas()),
      ]);

      this.usuariosCount.set(usuarios.countData ?? usuarios.data?.length ?? 0);
      this.ordenesCount.set(ordenes.countData ?? ordenes.data?.length ?? 0);
      this.pagosCount.set(pagos.countData ?? pagos.data?.length ?? 0);
      this.metricasCount.set(metricas.countData ?? metricas.data?.length ?? 0);
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo cargar el dashboard administrativo.'));
    }
  }
}
