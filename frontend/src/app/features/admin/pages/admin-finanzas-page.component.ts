import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { firstValueFrom } from 'rxjs';

import { AdminComision, AdminFactura, AdminPago } from '../../../core/models/admin.model';
import { AdminApiService } from '../../../core/services/admin-api.service';
import { getErrorMessage } from '../../../core/utils/http-error.util';

@Component({
  selector: 'app-admin-finanzas-page',
  standalone: true,
  imports: [CommonModule],
  template: `
    <section class="space-y-5">
      <header>
        <h1 class="text-2xl font-semibold">Finanzas administrativas</h1>
        <p class="text-sm text-slate-500">Pagos, comisiones y facturas con filtros base.</p>
      </header>

      <div class="flex flex-wrap gap-2">
        <button class="rounded-lg border px-3 py-1 text-sm" [class.bg-slate-900]="tab() === 'pagos'" [class.text-white]="tab() === 'pagos'" type="button" (click)="tab.set('pagos')">Pagos</button>
        <button class="rounded-lg border px-3 py-1 text-sm" [class.bg-slate-900]="tab() === 'comisiones'" [class.text-white]="tab() === 'comisiones'" type="button" (click)="tab.set('comisiones')">Comisiones</button>
        <button class="rounded-lg border px-3 py-1 text-sm" [class.bg-slate-900]="tab() === 'facturas'" [class.text-white]="tab() === 'facturas'" type="button" (click)="tab.set('facturas')">Facturas</button>
        <button class="rounded-lg border border-slate-300 px-3 py-1 text-sm" type="button" (click)="reload()">Recargar</button>
      </div>

      @if (errorMessage()) {
        <p class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ errorMessage() }}</p>
      }

      @if (tab() === 'pagos') {
        <article class="space-y-2 rounded-xl border border-slate-200 p-4">
          <h2 class="font-medium">Pagos ({{ pagos().length }})</h2>
          @for (p of pagos(); track p.id) {
            <p class="text-sm text-slate-600">{{ p.creado_en | date: 'short' }} · {{ p.estado }} · {{ p.metodo }} · Bs {{ p.monto }}</p>
          }
        </article>
      }

      @if (tab() === 'comisiones') {
        <article class="space-y-2 rounded-xl border border-slate-200 p-4">
          <h2 class="font-medium">Comisiones ({{ comisiones().length }})</h2>
          @for (c of comisiones(); track c.id) {
            <p class="text-sm text-slate-600">{{ c.creado_en | date: 'short' }} · {{ c.estado }} · Bs {{ c.monto_comision }}</p>
          }
        </article>
      }

      @if (tab() === 'facturas') {
        <article class="space-y-2 rounded-xl border border-slate-200 p-4">
          <h2 class="font-medium">Facturas ({{ facturas().length }})</h2>
          @for (f of facturas(); track f.id) {
            <p class="text-sm text-slate-600">{{ f.emitida_en | date: 'short' }} · {{ f.numero_factura }} · Bs {{ f.total }}</p>
          }
        </article>
      }
    </section>
  `,
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
