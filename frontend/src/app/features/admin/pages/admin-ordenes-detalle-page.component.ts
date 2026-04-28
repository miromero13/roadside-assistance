import { CommonModule } from '@angular/common';
import { Component, DestroyRef, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

import { AdminApiService } from '../../../core/services/admin-api.service';
import { AdminAsignacion, AdminAveria, AdminHistorialOrden, AdminOrden, AdminTaller } from '../../../core/models/admin.model';
import { getErrorMessage } from '../../../core/utils/http-error.util';
import { HlmTable } from '@spartan-ng/helm/table';

@Component({
  selector: 'app-admin-ordenes-detalle-page',
  standalone: true,
  imports: [CommonModule, HlmTable, RouterLink],
  templateUrl: './admin-ordenes-detalle-page.component.html',
})
export class AdminOrdenesDetallePageComponent {
  private readonly api = inject(AdminApiService);
  private readonly route = inject(ActivatedRoute);
  private readonly destroyRef = inject(DestroyRef);

  protected readonly orden = signal<AdminOrden | null>(null);
  protected readonly averia = signal<AdminAveria | null>(null);
  protected readonly taller = signal<AdminTaller | null>(null);
  protected readonly historial = signal<AdminHistorialOrden[]>([]);
  protected readonly asignaciones = signal<AdminAsignacion[]>([]);
  protected readonly errorMessage = signal('');

  constructor() {
    this.route.paramMap.pipe(takeUntilDestroyed(this.destroyRef)).subscribe((params) => {
      void this.loadDetalle(params.get('ordenId'));
    });
  }

  private async loadDetalle(ordenId: string | null): Promise<void> {
    if (!ordenId) {
      this.errorMessage.set('No se recibió una orden válida.');
      return;
    }

    this.errorMessage.set('');
    try {
      this.orden.set(null);
      this.averia.set(null);
      this.taller.set(null);
      this.historial.set([]);
      this.asignaciones.set([]);

      const ordenResponse = await firstValueFrom(this.api.getOrden(ordenId));
      const ordenActual = ordenResponse.data;

      if (!ordenActual) {
        throw new Error('La orden no tiene datos asociados.');
      }

      const { averia_id, taller_id } = ordenActual;
      if (!averia_id || !taller_id) {
        throw new Error('La orden no tiene avería o taller asociados.');
      }

      const [averiaResponse, tallerResponse, historialResponse, asignacionesResponse] = await Promise.all([
        firstValueFrom(this.api.getAveria(averia_id)),
        firstValueFrom(this.api.getTaller(taller_id)),
        firstValueFrom(this.api.getOrdenHistorial(ordenId)),
        firstValueFrom(this.api.getOrdenAsignaciones(ordenId)),
      ]);

      this.orden.set(ordenActual);
      this.averia.set(averiaResponse.data ?? null);
      this.taller.set(tallerResponse.data ?? null);
      this.historial.set(historialResponse.data ?? []);
      this.asignaciones.set(asignacionesResponse.data ?? []);
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo cargar el detalle de la orden.'));
    }
  }
}
