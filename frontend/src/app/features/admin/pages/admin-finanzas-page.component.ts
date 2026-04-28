import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { firstValueFrom } from 'rxjs';

import { AdminComision, AdminFactura, AdminPago } from '../../../core/models/admin.model';
import { AdminApiService } from '../../../core/services/admin-api.service';
import { getErrorMessage } from '../../../core/utils/http-error.util';
import { HlmTable } from '@spartan-ng/helm/table';

@Component({
  selector: 'app-admin-finanzas-page',
  standalone: true,
  imports: [CommonModule, HlmTable],
  templateUrl: './admin-finanzas-page.component.html',
})
export class AdminFinanzasPageComponent {
  private readonly api = inject(AdminApiService);

  protected readonly tab = signal<'pagos' | 'comisiones' | 'facturas'>('pagos');
  protected readonly pagos = signal<AdminPago[]>([]);
  protected readonly comisiones = signal<AdminComision[]>([]);
  protected readonly facturas = signal<AdminFactura[]>([]);
  protected readonly errorMessage = signal('');

  constructor() {
    void this.reload();
  }

  protected async reload(): Promise<void> {
    this.errorMessage.set('');
    try {
      const [pagosResponse, comisionesResponse, facturasResponse] = await Promise.all([
        firstValueFrom(this.api.listPagos()),
        firstValueFrom(this.api.listComisiones()),
        firstValueFrom(this.api.listFacturas()),
      ]);
      this.pagos.set(pagosResponse.data ?? []);
      this.comisiones.set(comisionesResponse.data ?? []);
      this.facturas.set(facturasResponse.data ?? []);
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo cargar la información financiera.'));
    }
  }
}
