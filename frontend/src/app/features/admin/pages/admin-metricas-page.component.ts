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
  templateUrl: './admin-metricas-page.component.html',
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
