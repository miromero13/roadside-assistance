import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';

import { TallerApiService } from '../../../core/services/taller-api.service';

@Component({
  selector: 'app-taller-home-page',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './taller-home-page.component.html',
})
export class TallerHomePageComponent {
  private readonly api = inject(TallerApiService);

  protected readonly pendientesCount = signal(0);
  protected readonly aceptadasCount = signal(0);
  protected readonly enProcesoCount = signal(0);
  protected readonly comisionesCount = signal(0);
  protected readonly errorMessage = signal('');

  constructor() {
    void this.loadSummary();
  }

  private async loadSummary(): Promise<void> {
    try {
      const [pendientes, aceptadas, enProceso, comisiones] = await Promise.all([
        firstValueFrom(this.api.listOrdenes('pendiente_respuesta')),
        firstValueFrom(this.api.listOrdenes('aceptada')),
        firstValueFrom(this.api.listOrdenes('en_proceso')),
        firstValueFrom(this.api.listComisionesMias()),
      ]);

      this.pendientesCount.set(pendientes.data?.length ?? 0);
      this.aceptadasCount.set(aceptadas.data?.length ?? 0);
      this.enProcesoCount.set(enProceso.data?.length ?? 0);
      this.comisionesCount.set(comisiones.data?.length ?? 0);
    } catch {
      this.errorMessage.set('No se pudo cargar el resumen del taller.');
    }
  }
}
