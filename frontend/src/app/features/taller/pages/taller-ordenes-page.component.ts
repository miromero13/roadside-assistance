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
  template: `
    <section class="space-y-5">
      <header class="space-y-1">
        <h1 class="text-2xl font-semibold">Órdenes del taller</h1>
        <p class="text-sm text-slate-500">Gestiona aceptación, rechazo y seguimiento operativo.</p>
      </header>

      <div class="flex flex-wrap gap-2">
        <button class="rounded-lg border px-3 py-1 text-sm" [class.bg-slate-900]="!estadoFiltro()" [class.text-white]="!estadoFiltro()" type="button" (click)="setFiltro('')">Todas</button>
        <button class="rounded-lg border px-3 py-1 text-sm" [class.bg-slate-900]="estadoFiltro()==='pendiente_respuesta'" [class.text-white]="estadoFiltro()==='pendiente_respuesta'" type="button" (click)="setFiltro('pendiente_respuesta')">Pendientes</button>
        <button class="rounded-lg border px-3 py-1 text-sm" [class.bg-slate-900]="estadoFiltro()==='aceptada'" [class.text-white]="estadoFiltro()==='aceptada'" type="button" (click)="setFiltro('aceptada')">Aceptadas</button>
        <button class="rounded-lg border px-3 py-1 text-sm" [class.bg-slate-900]="estadoFiltro()==='en_proceso'" [class.text-white]="estadoFiltro()==='en_proceso'" type="button" (click)="setFiltro('en_proceso')">En proceso</button>
      </div>

      @if (errorMessage()) {
        <p class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ errorMessage() }}</p>
      }

      <div class="space-y-2">
        @for (orden of ordenes(); track orden.id) {
          <article class="space-y-2 rounded-xl border border-slate-200 p-3">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <p class="font-medium">Orden {{ orden.id.slice(0, 8) }} · {{ orden.estado }}</p>
              <span class="text-xs text-slate-500">{{ orden.creado_en | date: 'short' }}</span>
            </div>
            <p class="text-sm text-slate-500">Avería: {{ orden.averia_id }} · Categoría: {{ orden.categoria_id }}</p>
            @if (orden.notas_conductor) {
              <p class="text-sm text-slate-700">{{ orden.notas_conductor }}</p>
            }

            <div class="flex flex-wrap gap-2">
              <a class="rounded-lg border border-slate-300 px-3 py-1 text-sm" [routerLink]="['/app/taller/ordenes', orden.id]">Ver detalle</a>
              @if (orden.estado === 'pendiente_respuesta') {
                <button class="rounded-lg bg-emerald-700 px-3 py-1 text-sm text-white" type="button" (click)="aceptarOrden(orden.id)">Aceptar</button>
                <button class="rounded-lg border border-red-300 px-3 py-1 text-sm text-red-700" type="button" (click)="setRechazoTarget(orden.id)">Rechazar</button>
              }
            </div>

            @if (rechazoTargetId() === orden.id) {
              <form class="mt-2 flex flex-wrap gap-2" [formGroup]="rechazoForm" (ngSubmit)="rechazarOrden()">
                <input class="min-w-[260px] flex-1 rounded-lg border border-slate-300 px-2 py-1 text-sm" formControlName="motivo" placeholder="Motivo de rechazo" />
                <button class="rounded-lg bg-slate-900 px-3 py-1 text-sm text-white" type="submit">Confirmar</button>
                <button class="rounded-lg border border-slate-300 px-3 py-1 text-sm" type="button" (click)="clearRechazoTarget()">Cancelar</button>
              </form>
            }
          </article>
        }

        @if (!ordenes().length) {
          <p class="rounded-lg border border-dashed border-slate-300 px-3 py-4 text-sm text-slate-500">No hay órdenes para el filtro seleccionado.</p>
        }
      </div>
    </section>
  `,
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
