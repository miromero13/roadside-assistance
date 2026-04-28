import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';

import { OrdenTaller } from '../../../core/models/taller.model';
import { TallerApiService } from '../../../core/services/taller-api.service';
import { getErrorMessage } from '../../../core/utils/http-error.util';

@Component({
  selector: 'app-taller-ordenes-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './taller-ordenes-page.component.html',
})
export class TallerOrdenesPageComponent {
  private readonly api = inject(TallerApiService);
  private readonly fb = inject(FormBuilder);

  protected readonly ordenes = signal<OrdenTaller[]>([]);
  protected readonly estadoFiltro = signal('');
  protected readonly errorMessage = signal('');

  protected readonly rechazoTargetId = signal<string | null>(null);
  protected readonly rechazoForm = this.fb.nonNullable.group({
    motivo: ['', [Validators.required, Validators.minLength(3)]],
  });

  constructor() {
    void this.loadOrdenes();
  }

  protected async setFiltro(estado: string): Promise<void> {
    this.estadoFiltro.set(estado);
    await this.loadOrdenes();
  }

  protected async aceptarOrden(ordenId: string): Promise<void> {
    this.errorMessage.set('');
    try {
      await firstValueFrom(
        this.api.aceptarOrden(ordenId, {
          tiempo_estimado_respuesta_min: 20,
          tiempo_estimado_llegada_min: 35,
          notas_taller: 'Orden aceptada desde web taller',
        }),
      );
      await this.loadOrdenes();
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo aceptar la orden.'));
    }
  }

  protected setRechazoTarget(ordenId: string): void {
    this.rechazoTargetId.set(ordenId);
    this.rechazoForm.reset({ motivo: '' });
  }

  protected clearRechazoTarget(): void {
    this.rechazoTargetId.set(null);
    this.rechazoForm.reset({ motivo: '' });
  }

  protected async rechazarOrden(): Promise<void> {
    const ordenId = this.rechazoTargetId();
    if (!ordenId || this.rechazoForm.invalid) {
      this.rechazoForm.markAllAsTouched();
      return;
    }

    this.errorMessage.set('');
    try {
      await firstValueFrom(this.api.rechazarOrden(ordenId, this.rechazoForm.getRawValue().motivo));
      this.clearRechazoTarget();
      await this.loadOrdenes();
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo rechazar la orden.'));
    }
  }

  private async loadOrdenes(): Promise<void> {
    this.errorMessage.set('');
    try {
      const response = await firstValueFrom(this.api.listOrdenes(this.estadoFiltro() || undefined));
      this.ordenes.set(response.data ?? []);
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudieron cargar las órdenes del taller.'));
    }
  }
}
