import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';

import { ConductorApiService } from '../../../core/services/conductor-api.service';

@Component({
  selector: 'app-conductor-home-page',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './conductor-home-page.component.html',
})
export class ConductorHomePageComponent {
  private readonly api = inject(ConductorApiService);

  protected readonly vehiculosCount = signal(0);
  protected readonly averiasCount = signal(0);
  protected readonly ordenesCount = signal(0);
  protected readonly noLeidasCount = signal(0);
  protected readonly errorMessage = signal('');

  constructor() {
    void this.loadSummary();
  }

  private async loadSummary(): Promise<void> {
    try {
      const [vehiculos, averias, ordenes, notificaciones] = await Promise.all([
        firstValueFrom(this.api.listVehiculos()),
        firstValueFrom(this.api.listAverias()),
        firstValueFrom(this.api.listOrdenes()),
        firstValueFrom(this.api.listNotificaciones(true)),
      ]);

      this.vehiculosCount.set(vehiculos.data?.length ?? 0);
      this.averiasCount.set(averias.data?.length ?? 0);
      this.ordenesCount.set(ordenes.data?.length ?? 0);
      this.noLeidasCount.set(notificaciones.data?.length ?? 0);
    } catch {
      this.errorMessage.set('No se pudo cargar el resumen del conductor.');
    }
  }
}
