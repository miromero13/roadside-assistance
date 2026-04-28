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
  templateUrl: './mecanico-asignacion-detalle-page.component.html',
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
