import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { firstValueFrom } from 'rxjs';

import {
  AdminAsignacion,
  AdminHistorialOrden,
  AdminOrden,
} from '../../../core/models/admin.model';
import { AdminApiService } from '../../../core/services/admin-api.service';
import { getErrorMessage } from '../../../core/utils/http-error.util';

@Component({
  selector: 'app-admin-ordenes-page',
  standalone: true,
  imports: [CommonModule],
  template: `
    <section class="space-y-5">
      <header>
        <h1 class="text-2xl font-semibold">Supervisión de órdenes</h1>
        <p class="text-sm text-slate-500">Consulta órdenes, historial y asignaciones.</p>
      </header>

      <div class="flex flex-wrap gap-2">
        <button class="rounded-lg border px-3 py-1 text-sm" [class.bg-slate-900]="filtroEstado() === ''" [class.text-white]="filtroEstado() === ''" type="button" (click)="setFiltro('')">Todas</button>
        <button class="rounded-lg border px-3 py-1 text-sm" [class.bg-slate-900]="filtroEstado() === 'pendiente_respuesta'" [class.text-white]="filtroEstado() === 'pendiente_respuesta'" type="button" (click)="setFiltro('pendiente_respuesta')">Pendiente</button>
        <button class="rounded-lg border px-3 py-1 text-sm" [class.bg-slate-900]="filtroEstado() === 'en_camino'" [class.text-white]="filtroEstado() === 'en_camino'" type="button" (click)="setFiltro('en_camino')">En camino</button>
        <button class="rounded-lg border px-3 py-1 text-sm" [class.bg-slate-900]="filtroEstado() === 'en_proceso'" [class.text-white]="filtroEstado() === 'en_proceso'" type="button" (click)="setFiltro('en_proceso')">En proceso</button>
        <button class="rounded-lg border px-3 py-1 text-sm" [class.bg-slate-900]="filtroEstado() === 'completada'" [class.text-white]="filtroEstado() === 'completada'" type="button" (click)="setFiltro('completada')">Completada</button>
      </div>

      @if (errorMessage()) {
        <p class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ errorMessage() }}</p>
      }

      <div class="space-y-2">
        @for (orden of ordenes(); track orden.id) {
          <article class="space-y-2 rounded-xl border border-slate-200 p-3">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <p class="font-medium">Orden {{ orden.id.slice(0, 8) }} · {{ orden.estado }}</p>
              <span class="text-xs text-slate-500">{{ orden.creado_en | date: 'short' }}</span>
            </div>
            <p class="text-sm text-slate-500">Avería {{ orden.averia_id }} · Taller {{ orden.taller_id }}</p>
            <button class="rounded-lg border border-slate-300 px-3 py-1 text-sm" type="button" (click)="verDetalle(orden.id)">Ver historial/asignaciones</button>
          </article>
        }
      </div>

      @if (ordenSeleccionadaId()) {
        <article class="space-y-2 rounded-xl border border-slate-200 p-4">
          <h2 class="font-medium">Detalle de orden {{ ordenSeleccionadaId() }}</h2>
          <p class="text-sm font-medium">Historial</p>
          @for (h of historial(); track h.id) {
            <p class="text-sm text-slate-600">{{ h.creado_en | date: 'short' }} · {{ h.estado_anterior ?? '-' }} -> {{ h.estado_nuevo }} · {{ h.observacion ?? 'sin observación' }}</p>
          }
          @if (!historial().length) {
            <p class="text-sm text-slate-500">Sin historial.</p>
          }

          <p class="pt-2 text-sm font-medium">Asignaciones</p>
          @for (a of asignaciones(); track a.id) {
            <p class="text-sm text-slate-600">{{ a.asignado_en | date: 'short' }} · mecánico {{ a.mecanico_id }} · {{ a.estado }}</p>
          }
          @if (!asignaciones().length) {
            <p class="text-sm text-slate-500">Sin asignaciones.</p>
          }
        </article>
      }
    </section>
  `,
})
export class AdminOrdenesPageComponent {
  private readonly api = inject(AdminApiService);

  protected readonly ordenes = signal<AdminOrden[]>([]);
  protected readonly filtroEstado = signal('');
  protected readonly ordenSeleccionadaId = signal<string | null>(null);
  protected readonly historial = signal<AdminHistorialOrden[]>([]);
  protected readonly asignaciones = signal<AdminAsignacion[]>([]);
  protected readonly errorMessage = signal('');

  constructor() {
    void this.loadOrdenes();
  }

  protected async setFiltro(estado: string): Promise<void> {
    this.filtroEstado.set(estado);
    await this.loadOrdenes();
  }

  protected async verDetalle(ordenId: string): Promise<void> {
    this.errorMessage.set('');
    this.ordenSeleccionadaId.set(ordenId);
    try {
      const [historialResponse, asignacionesResponse] = await Promise.all([
        firstValueFrom(this.api.getOrdenHistorial(ordenId)),
        firstValueFrom(this.api.getOrdenAsignaciones(ordenId)),
      ]);
      this.historial.set(historialResponse.data ?? []);
      this.asignaciones.set(asignacionesResponse.data ?? []);
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo cargar el detalle de la orden.'));
    }
  }

  private async loadOrdenes(): Promise<void> {
    this.errorMessage.set('');
    try {
      const response = await firstValueFrom(this.api.listOrdenes(this.filtroEstado() || undefined));
      this.ordenes.set(response.data ?? []);
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudieron cargar las órdenes.'));
    }
  }
}
