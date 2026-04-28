import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';

import { Notificacion } from '../../../core/models/conductor.model';
import { ConductorApiService } from '../../../core/services/conductor-api.service';
import { getErrorMessage } from '../../../core/utils/http-error.util';

@Component({
  selector: 'app-conductor-notificaciones-page',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './conductor-notificaciones-page.component.html',
})
export class ConductorNotificacionesPageComponent {
  private readonly api = inject(ConductorApiService);

  protected readonly notificaciones = signal<Notificacion[]>([]);
  protected readonly soloNoLeidas = signal(false);
  protected readonly errorMessage = signal('');

  constructor() {
    void this.load();
  }

  protected async toggleFiltroNoLeidas(): Promise<void> {
    this.soloNoLeidas.set(!this.soloNoLeidas());
    await this.load();
  }

  protected async marcarLeida(notificacionId: string): Promise<void> {
    this.errorMessage.set('');
    try {
      await firstValueFrom(this.api.marcarNotificacionLeida(notificacionId));
      await this.load();
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo marcar la notificación como leída.'));
    }
  }

  protected async marcarTodas(): Promise<void> {
    this.errorMessage.set('');
    try {
      await firstValueFrom(this.api.marcarTodasNotificacionesLeidas());
      await this.load();
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudieron marcar todas las notificaciones.'));
    }
  }

  private async load(): Promise<void> {
    this.errorMessage.set('');
    try {
      const response = await firstValueFrom(this.api.listNotificaciones(this.soloNoLeidas()));
      this.notificaciones.set(response.data ?? []);
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudieron cargar las notificaciones.'));
    }
  }
}
