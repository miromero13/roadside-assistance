import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { lucideMoreVertical } from '@ng-icons/lucide';

import { AdminOrden } from '../../../core/models/admin.model';
import { AdminApiService } from '../../../core/services/admin-api.service';
import { getErrorMessage } from '../../../core/utils/http-error.util';
import { HlmIcon } from '@spartan-ng/helm/icon';
import { HlmTable } from '@spartan-ng/helm/table';
import { HlmButton } from '@spartan-ng/helm/button';

@Component({
  selector: 'app-admin-ordenes-page',
  standalone: true,
  imports: [CommonModule, HlmButton, HlmIcon, HlmTable, NgIcon, RouterLink],
  providers: [provideIcons({ lucideMoreVertical })],
  templateUrl: './admin-ordenes-page.component.html',
})
export class AdminOrdenesPageComponent {
  private readonly api = inject(AdminApiService);

  protected readonly ordenes = signal<AdminOrden[]>([]);
  protected readonly filtroEstado = signal('');
  protected readonly errorMessage = signal('');
  protected readonly actionMenuOpenId = signal<string | null>(null);

  constructor() {
    void this.loadOrdenes();
  }

  protected async setFiltro(estado: string): Promise<void> {
    this.filtroEstado.set(estado);
    this.actionMenuOpenId.set(null);
    await this.loadOrdenes();
  }

  protected toggleActionMenu(ordenId: string): void {
    this.actionMenuOpenId.set(this.actionMenuOpenId() === ordenId ? null : ordenId);
  }

  private async loadOrdenes(): Promise<void> {
    this.errorMessage.set('');
    try {
      const response = await firstValueFrom(this.api.listOrdenes(this.filtroEstado() || undefined));
      this.ordenes.set(response.data ?? []);
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudieron cargar las órdenes.'));
    }
  }
}
