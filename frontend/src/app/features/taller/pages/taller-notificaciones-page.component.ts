import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';

import { TallerApiService } from '../../../core/services/taller-api.service';
import { getErrorMessage } from '../../../core/utils/http-error.util';

@Component({
  selector: 'app-taller-notificaciones-page',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <section class="space-y-5">
      <header class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 class="text-2xl font-semibold">Notificaciones Taller</h1>
          <p class="text-sm text-slate-500">Eventos operativos de órdenes, presupuestos y chat.</p>
        </div>
        <div class="flex gap-2">
          <button class="rounded-lg border border-slate-300 px-3 py-2 text-sm" type="button" (click)="toggleFiltroNoLeidas()">
            {{ soloNoLeidas() ? 'Ver todas' : 'Solo no leídas' }}
          </button>
          <button class="rounded-lg bg-slate-900 px-3 py-2 text-sm text-white" type="button" (click)="marcarTodas()">
            Marcar todas leídas
          </button>
        </div>
      </header>

      @if (errorMessage()) {
        <p class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ errorMessage() }}</p>
      }

      <div class="space-y-2">
        @for (item of notificaciones(); track item.id) {
          <article class="space-y-2 rounded-xl border p-3" [class.border-slate-200]="item.leida" [class.border-amber-300]="!item.leida">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <p class="font-medium">{{ item.titulo }}</p>
              <span class="text-xs text-slate-500">{{ item.creado_en | date: 'short' }}</span>
            </div>
            <p class="text-sm text-slate-700">{{ item.mensaje }}</p>
            <div class="flex flex-wrap gap-2 text-sm">
              @if (item.orden_id) {
                <a class="rounded-lg border border-slate-300 px-3 py-1" [routerLink]="['/app/taller/ordenes', item.orden_id]">Ver orden</a>
              }
              @if (!item.leida) {
                <button class="rounded-lg border border-slate-300 px-3 py-1" type="button" (click)="marcarLeida(item.id)">Marcar leída</button>
              }
            </div>
          </article>
        }

        @if (!notificaciones().length) {
          <p class="rounded-lg border border-dashed border-slate-300 px-3 py-4 text-sm text-slate-500">No hay notificaciones para mostrar.</p>
        }
      </div>
    </section>
  `,
})
export class TallerNotificacionesPageComponent {
  private readonly api = inject(TallerApiService);

  protected readonly notificaciones = signal<
    Array<{
      id: string;
      usuario_id: string;
      orden_id: string | null;
      titulo: string;
      mensaje: string;
      tipo: string;
      leida: boolean;
      creado_en: string;
    }>
  >([]);
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
      this.errorMessage.set(getErrorMessage(error, 'No se pudieron cargar las notificaciones del taller.'));
    }
  }
}
