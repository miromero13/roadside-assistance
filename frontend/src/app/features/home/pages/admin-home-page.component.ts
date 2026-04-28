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
  templateUrl: './admin-home-page.component.html',
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
