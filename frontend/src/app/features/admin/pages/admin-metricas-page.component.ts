import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { firstValueFrom } from 'rxjs';

import { AdminMetrica } from '../../../core/models/admin.model';
import { AdminApiService } from '../../../core/services/admin-api.service';
import { getErrorMessage } from '../../../core/utils/http-error.util';

@Component({
  selector: 'app-admin-metricas-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <section class="space-y-5">
      <header>
        <h1 class="text-2xl font-semibold">Métricas operativas</h1>
        <p class="text-sm text-slate-500">Consulta indicadores de servicio y recalcula por orden.</p>
      </header>

      <form class="grid gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4 sm:grid-cols-[1fr_auto]" [formGroup]="recalculoForm" (ngSubmit)="recalcularMetrica()">
        <input class="rounded-lg border border-slate-300 px-3 py-2" placeholder="Orden ID para recalcular" formControlName="ordenId" />
        <button class="w-fit rounded-lg bg-slate-900 px-4 py-2 text-sm text-white" type="submit">Recalcular</button>
      </form>

      @if (errorMessage()) {
        <p class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ errorMessage() }}</p>
      }
      @if (successMessage()) {
        <p class="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">{{ successMessage() }}</p>
      }

      <article class="space-y-2 rounded-xl border border-slate-200 p-4">
        <h2 class="font-medium">Listado de métricas ({{ metricas().length }})</h2>
        @for (m of metricas(); track m.id) {
          <p class="text-sm text-slate-600">
            {{ m.creado_en | date: 'short' }} · orden {{ m.orden_id }} · resp {{ m.tiempo_respuesta_min ?? 'N/A' }} min ·
            llegada {{ m.tiempo_llegada_min ?? 'N/A' }} min ·
            resolución {{ m.tiempo_resolucion_min ?? 'N/A' }} min ·
            calif {{ m.calificacion_final ?? 'N/A' }}
          </p>
        }
      </article>
    </section>
  `,
})
export class AdminMetricasPageComponent {
  private readonly api = inject(AdminApiService);
  private readonly fb = inject(FormBuilder);

  protected readonly metricas = signal<AdminMetrica[]>([]);
  protected readonly errorMessage = signal('');
  protected readonly successMessage = signal('');

  protected readonly recalculoForm = this.fb.nonNullable.group({
    ordenId: '',
  });

  constructor() {
    void this.loadMetricas();
  }

  protected async recalcularMetrica(): Promise<void> {
    const { ordenId } = this.recalculoForm.getRawValue();
    if (!ordenId.trim()) {
      this.errorMessage.set('Ingresa un orden_id para recalcular.');
      return;
    }

    this.errorMessage.set('');
    this.successMessage.set('');
    try {
      await firstValueFrom(this.api.recalcularMetricaOrden(ordenId.trim()));
      this.successMessage.set('Métrica recalculada correctamente.');
      await this.loadMetricas();
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo recalcular la métrica.'));
    }
  }

  private async loadMetricas(): Promise<void> {
    this.errorMessage.set('');
    try {
      const response = await firstValueFrom(this.api.listMetricas());
      this.metricas.set(response.data ?? []);
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudieron cargar las métricas.'));
    }
  }
}
