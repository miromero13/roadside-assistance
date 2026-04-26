import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { firstValueFrom } from 'rxjs';

import {
  AsignacionMecanico,
  EstadoAsignacionMecanico,
  HistorialOrdenMecanico,
  OrdenMecanico,
} from '../../../core/models/mecanico.model';
import { MecanicoApiService } from '../../../core/services/mecanico-api.service';
import { getErrorMessage } from '../../../core/utils/http-error.util';

@Component({
  selector: 'app-mecanico-asignacion-detalle-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  template: `
    <section class="space-y-5">
      <a class="inline-flex items-center rounded-lg border border-slate-300 px-3 py-1 text-sm" routerLink="/app/mecanico/asignaciones">← Volver a asignaciones</a>

      <header>
        <h1 class="text-2xl font-semibold">Detalle de asignación</h1>
        <p class="text-sm text-slate-500">Actualiza tu estado operativo y registra observaciones técnicas.</p>
      </header>

      @if (errorMessage()) {
        <p class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ errorMessage() }}</p>
      }

      @if (successMessage()) {
        <p class="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">{{ successMessage() }}</p>
      }

      @if (asignacion()) {
        <article class="space-y-2 rounded-xl border border-slate-200 p-4">
          <p class="font-medium">Asignación {{ asignacion()!.id.slice(0, 8) }} · {{ asignacion()!.estado }}</p>
          <p class="text-sm text-slate-500">Orden: {{ asignacion()!.orden_id }}</p>
          @if (asignacion()!.notas) {
            <p class="text-sm text-slate-700">{{ asignacion()!.notas }}</p>
          }
        </article>
      }

      @if (orden()) {
        <article class="space-y-2 rounded-xl border border-slate-200 p-4">
          <h2 class="font-medium">Incidente asignado</h2>
          <p class="text-sm">Orden {{ orden()!.id.slice(0, 8) }} · Estado {{ orden()!.estado }}</p>
          <p class="text-sm text-slate-600">Avería: {{ orden()!.averia_id }}</p>
          <p class="text-sm text-slate-600">Taller: {{ orden()!.taller_id }}</p>
          <p class="text-sm text-slate-600">Categoría: {{ orden()!.categoria_id }}</p>
          <p class="text-sm text-slate-600">ETA llegada: {{ orden()!.tiempo_estimado_llegada_min ?? 'N/A' }} min</p>
          @if (orden()!.notas_conductor) {
            <p class="text-sm text-slate-700">Nota conductor: {{ orden()!.notas_conductor }}</p>
          }
          @if (orden()!.notas_taller) {
            <p class="text-sm text-slate-700">Nota taller: {{ orden()!.notas_taller }}</p>
          }
        </article>
      }

      <form class="grid gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4" [formGroup]="estadoForm" (ngSubmit)="actualizarEstado()">
        <h2 class="font-medium">Actualizar estado operativo</h2>
        <select class="rounded-lg border border-slate-300 px-3 py-2" formControlName="estado">
          @for (estado of estadosDisponibles(); track estado) {
            <option [value]="estado">{{ estado }}</option>
          }
        </select>
        <textarea class="rounded-lg border border-slate-300 px-3 py-2" rows="2" placeholder="Observación técnica" formControlName="notas"></textarea>
        <button class="w-fit rounded-lg bg-slate-900 px-4 py-2 text-sm text-white" type="submit">Guardar estado</button>
      </form>

      <article class="space-y-2 rounded-xl border border-slate-200 p-4">
        <h2 class="font-medium">Historial de la orden</h2>
        @for (item of historial(); track item.id) {
          <p class="text-sm text-slate-600">{{ item.creado_en | date: 'short' }} · {{ item.estado_anterior ?? '-' }} → {{ item.estado_nuevo }} · {{ item.observacion ?? 'Sin observación' }}</p>
        }
        @if (!historial().length) {
          <p class="text-sm text-slate-500">No hay historial disponible.</p>
        }
      </article>
    </section>
  `,
})
export class MecanicoAsignacionDetallePageComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly api = inject(MecanicoApiService);
  private readonly fb = inject(FormBuilder);

  protected readonly asignacion = signal<AsignacionMecanico | null>(null);
  protected readonly orden = signal<OrdenMecanico | null>(null);
  protected readonly historial = signal<HistorialOrdenMecanico[]>([]);
  protected readonly errorMessage = signal('');
  protected readonly successMessage = signal('');
  protected readonly estadosDisponibles = signal<EstadoAsignacionMecanico[]>([]);

  protected readonly estadoForm = this.fb.nonNullable.group({
    estado: 'asignado' as EstadoAsignacionMecanico,
    notas: '',
  });

  constructor() {
    void this.load();
  }

  protected async actualizarEstado(): Promise<void> {
    const current = this.asignacion();
    if (!current) {
      return;
    }

    this.errorMessage.set('');
    this.successMessage.set('');
    const payload = this.estadoForm.getRawValue();
    try {
      const response = await firstValueFrom(
        this.api.updateEstadoAsignacion(current.id, payload.estado, payload.notas),
      );
      this.asignacion.set(response.data ?? current);
      this.computeEstadosDisponibles(response.data?.estado ?? current.estado);
      this.successMessage.set('Estado actualizado correctamente.');
      await this.loadOrdenContext(current.orden_id);
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo actualizar el estado de la asignación.'));
    }
  }

  private async load(): Promise<void> {
    const asignacionId = this.route.snapshot.paramMap.get('asignacionId');
    if (!asignacionId) {
      this.errorMessage.set('No se encontró identificador de asignación.');
      return;
    }

    this.errorMessage.set('');
    try {
      const response = await firstValueFrom(this.api.getAsignacion(asignacionId));
      const asignacion = response.data;
      if (!asignacion) {
        this.errorMessage.set('No se pudo cargar la asignación.');
        return;
      }
      this.asignacion.set(asignacion);
      this.computeEstadosDisponibles(asignacion.estado);
      this.estadoForm.patchValue({
        estado: (this.estadosDisponibles()[0] ?? asignacion.estado) as EstadoAsignacionMecanico,
      });
      await this.loadOrdenContext(asignacion.orden_id);
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo cargar el detalle de asignación.'));
    }
  }

  private async loadOrdenContext(ordenId: string): Promise<void> {
    const [ordenResponse, historialResponse] = await Promise.all([
      firstValueFrom(this.api.getOrden(ordenId)),
      firstValueFrom(this.api.listHistorialOrden(ordenId)),
    ]);
    this.orden.set(ordenResponse.data ?? null);
    this.historial.set(historialResponse.data ?? []);
  }

  private computeEstadosDisponibles(actual: EstadoAsignacionMecanico): void {
    const transiciones: Record<EstadoAsignacionMecanico, EstadoAsignacionMecanico[]> = {
      asignado: ['en_camino', 'cancelado'],
      en_camino: ['atendiendo', 'cancelado'],
      atendiendo: ['finalizado', 'cancelado'],
      finalizado: [],
      cancelado: [],
    };
    const options = transiciones[actual] ?? [];
    this.estadosDisponibles.set(options);
    this.estadoForm.patchValue({ estado: options[0] ?? actual });
  }
}
