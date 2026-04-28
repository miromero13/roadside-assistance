import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { firstValueFrom } from 'rxjs';

import { ComisionTaller } from '../../../core/models/taller.model';
import { TallerApiService } from '../../../core/services/taller-api.service';
import { getErrorMessage } from '../../../core/utils/http-error.util';

@Component({
  selector: 'app-taller-comisiones-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './taller-comisiones-page.component.html',
})
export class TallerComisionesPageComponent {
  private readonly api = inject(TallerApiService);

  protected readonly comisiones = signal<ComisionTaller[]>([]);
  protected readonly errorMessage = signal('');

  constructor() {
    void this.load();
  }

  protected async pagar(comisionId: string): Promise<void> {
    this.errorMessage.set('');
    try {
      await firstValueFrom(this.api.pagarComision(comisionId));
      await this.load();
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo pagar la comisión.'));
    }
  }

  private async load(): Promise<void> {
    this.errorMessage.set('');
    try {
      const response = await firstValueFrom(this.api.listComisionesMias());
      this.comisiones.set(response.data ?? []);
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudieron cargar las comisiones.'));
    }
  }
}
