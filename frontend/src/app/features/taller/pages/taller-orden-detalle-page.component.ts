import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { firstValueFrom } from 'rxjs';

import {
  AsignacionOrdenTaller,
  MecanicoTaller,
  OrdenTaller,
  PresupuestoTaller,
} from '../../../core/models/taller.model';
import { TallerApiService } from '../../../core/services/taller-api.service';
import { getErrorMessage } from '../../../core/utils/http-error.util';

@Component({
  selector: 'app-taller-orden-detalle-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  template: `
    <section class="space-y-5">
      <a routerLink="/app/taller/ordenes" class="text-sm text-slate-600 underline">← Volver a órdenes</a>

      <header class="space-y-1">
        <h1 class="text-2xl font-semibold">Detalle orden taller</h1>
        @if (orden()) {
          <p class="text-sm text-slate-500">Estado: {{ orden()?.estado }} · Avería: {{ orden()?.averia_id }}</p>
        }
      </header>

      @if (errorMessage()) {
        <p class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ errorMessage() }}</p>
      }

      <section class="space-y-3 rounded-xl border border-slate-200 p-4">
        <h2 class="font-medium">Asignación de mecánico</h2>
        <form class="flex flex-wrap items-end gap-3" [formGroup]="asignacionForm" (ngSubmit)="asignarMecanico()">
          <label class="space-y-1 text-sm min-w-[280px]">
            <span>Mecánico disponible</span>
            <select class="w-full rounded-lg border border-slate-300 px-3 py-2" formControlName="mecanico_id">
              <option value="">Selecciona mecánico</option>
              @for (mecanico of mecanicos(); track mecanico.id) {
                <option [value]="mecanico.id">{{ mecanico.id.slice(0, 8) }} · {{ mecanico.especialidad || 'General' }} · {{ mecanico.disponible ? 'Disponible' : 'No disponible' }}</option>
              }
            </select>
          </label>
          <label class="space-y-1 text-sm min-w-[260px] flex-1">
            <span>Notas</span>
            <input class="w-full rounded-lg border border-slate-300 px-3 py-2" formControlName="notas" placeholder="Notas de asignación" />
          </label>
          <button class="rounded-lg bg-slate-900 px-4 py-2 text-sm text-white" type="submit">Asignar</button>
        </form>

        <div class="space-y-2">
          @for (asignacion of asignaciones(); track asignacion.id) {
            <article class="rounded-lg bg-slate-50 p-2 text-sm">
              <p class="font-medium">Mecánico: {{ asignacion.mecanico_id }}</p>
              <p class="text-slate-500">Estado: {{ asignacion.estado }} · {{ asignacion.asignado_en | date: 'short' }}</p>
            </article>
          }
          @if (!asignaciones().length) {
            <p class="text-sm text-slate-500">No hay asignaciones registradas para esta orden.</p>
          }
        </div>
      </section>

      <section class="space-y-3 rounded-xl border border-slate-200 p-4">
        <h2 class="font-medium">Crear presupuesto</h2>
        <form class="grid gap-3" [formGroup]="presupuestoForm" (ngSubmit)="crearPresupuesto()">
          <textarea class="rounded-lg border border-slate-300 px-3 py-2" rows="2" placeholder="Descripción de trabajos" formControlName="descripcion_trabajos"></textarea>
          <div class="grid gap-3 sm:grid-cols-2">
            <input class="rounded-lg border border-slate-300 px-3 py-2" type="number" formControlName="monto_repuestos" placeholder="Monto repuestos" />
            <input class="rounded-lg border border-slate-300 px-3 py-2" type="number" formControlName="monto_mano_obra" placeholder="Monto mano de obra" />
          </div>
          <button class="w-fit rounded-lg bg-slate-900 px-4 py-2 text-sm text-white" type="submit">Crear presupuesto</button>
        </form>

        <div class="space-y-2">
          @for (presupuesto of presupuestos(); track presupuesto.id) {
            <article class="rounded-lg bg-slate-50 p-3 text-sm">
              <p class="font-medium">Versión {{ presupuesto.version }} · {{ presupuesto.estado }}</p>
              <p class="text-slate-600">{{ presupuesto.descripcion_trabajos }}</p>
              <p class="text-slate-500">Total: Bs {{ presupuesto.monto_total }}</p>
            </article>
          }
          @if (!presupuestos().length) {
            <p class="text-sm text-slate-500">Aún no hay presupuestos para esta orden.</p>
          }
        </div>
      </section>

      <section class="space-y-3 rounded-xl border border-slate-200 p-4">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <h2 class="font-medium">Chat de la orden</h2>
          <div class="flex gap-2 text-sm">
            <span class="rounded-full bg-slate-100 px-3 py-1">No leídos: {{ chatNoLeidos() }}</span>
            <button class="rounded-lg border border-slate-300 px-3 py-1" type="button" (click)="marcarChatLeido()">Marcar todo leído</button>
          </div>
        </div>

        <form class="flex flex-wrap items-end gap-2" [formGroup]="chatForm" (ngSubmit)="enviarMensajeChat()">
          <label class="min-w-[280px] flex-1 space-y-1 text-sm">
            <span>Mensaje</span>
            <input class="w-full rounded-lg border border-slate-300 px-3 py-2" formControlName="contenido" placeholder="Escribe un mensaje" />
          </label>
          <button class="rounded-lg bg-slate-900 px-4 py-2 text-sm text-white" type="submit">Enviar</button>
          <button class="rounded-lg border border-slate-300 px-4 py-2 text-sm" type="button" (click)="cargarChat()">Actualizar</button>
        </form>

        <div class="max-h-72 space-y-2 overflow-auto rounded-lg border border-slate-200 p-2">
          @for (mensaje of mensajes(); track mensaje.id) {
            <article class="rounded-lg bg-slate-50 p-2 text-sm">
              <div class="flex flex-wrap items-center justify-between gap-2">
                <p class="font-medium">{{ mensaje.remitente_id }}</p>
                <span class="text-xs text-slate-500">{{ mensaje.enviado_en | date: 'short' }}</span>
              </div>
              <p class="text-slate-700">{{ mensaje.contenido || '(sin contenido)' }}</p>
              @if (!mensaje.leido) {
                <button class="mt-1 rounded-lg border border-slate-300 px-2 py-0.5 text-xs" type="button" (click)="marcarMensajeLeido(mensaje.id)">Marcar leído</button>
              }
            </article>
          }
          @if (!mensajes().length) {
            <p class="text-sm text-slate-500">No hay mensajes en este chat aún.</p>
          }
        </div>
      </section>
    </section>
  `,
})
export class TallerOrdenDetallePageComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly api = inject(TallerApiService);
  private readonly fb = inject(FormBuilder);

  protected readonly orden = signal<OrdenTaller | null>(null);
  protected readonly asignaciones = signal<AsignacionOrdenTaller[]>([]);
  protected readonly presupuestos = signal<PresupuestoTaller[]>([]);
  protected readonly mecanicos = signal<MecanicoTaller[]>([]);
  protected readonly chatId = signal<string | null>(null);
  protected readonly mensajes = signal<
    Array<{
      id: string;
      chat_id: string;
      remitente_id: string;
      contenido: string | null;
      tipo: string;
      media_url: string | null;
      leido: boolean;
      enviado_en: string;
    }>
  >([]);
  protected readonly chatNoLeidos = signal(0);
  protected readonly errorMessage = signal('');

  protected readonly asignacionForm = this.fb.nonNullable.group({
    mecanico_id: ['', [Validators.required]],
    notas: ['Asignado desde web taller'],
  });

  protected readonly presupuestoForm = this.fb.nonNullable.group({
    descripcion_trabajos: ['', [Validators.required, Validators.minLength(3)]],
    monto_repuestos: [0, [Validators.required]],
    monto_mano_obra: [0, [Validators.required]],
  });

  protected readonly chatForm = this.fb.nonNullable.group({
    contenido: ['', [Validators.required, Validators.minLength(1)]],
  });

  constructor() {
    void this.loadAll();
  }

  protected async asignarMecanico(): Promise<void> {
    if (this.asignacionForm.invalid) {
      this.asignacionForm.markAllAsTouched();
      return;
    }
    const ordenId = this.route.snapshot.paramMap.get('ordenId');
    if (!ordenId) {
      return;
    }
    this.errorMessage.set('');
    try {
      const payload = this.asignacionForm.getRawValue();
      await firstValueFrom(this.api.asignarMecanico(ordenId, payload.mecanico_id, payload.notas));
      await this.loadAll();
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo asignar el mecánico.'));
    }
  }

  protected async crearPresupuesto(): Promise<void> {
    if (this.presupuestoForm.invalid) {
      this.presupuestoForm.markAllAsTouched();
      return;
    }
    const ordenId = this.route.snapshot.paramMap.get('ordenId');
    if (!ordenId) {
      return;
    }
    this.errorMessage.set('');
    try {
      const payload = this.presupuestoForm.getRawValue();
      await firstValueFrom(
        this.api.crearPresupuesto(ordenId, {
          descripcion_trabajos: payload.descripcion_trabajos,
          items_detalle: { items: [] },
          monto_repuestos: payload.monto_repuestos,
          monto_mano_obra: payload.monto_mano_obra,
        }),
      );
      await this.loadAll();
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo crear el presupuesto.'));
    }
  }

  protected async enviarMensajeChat(): Promise<void> {
    if (this.chatForm.invalid || !this.chatId()) {
      this.chatForm.markAllAsTouched();
      return;
    }
    this.errorMessage.set('');
    try {
      await firstValueFrom(this.api.enviarMensaje(this.chatId()!, this.chatForm.getRawValue().contenido));
      this.chatForm.reset({ contenido: '' });
      await this.cargarChat();
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo enviar el mensaje de chat.'));
    }
  }

  protected async marcarMensajeLeido(mensajeId: string): Promise<void> {
    if (!this.chatId()) {
      return;
    }
    this.errorMessage.set('');
    try {
      await firstValueFrom(this.api.marcarMensajeLeido(this.chatId()!, mensajeId));
      await this.cargarChat();
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo marcar el mensaje como leído.'));
    }
  }

  protected async marcarChatLeido(): Promise<void> {
    if (!this.chatId()) {
      return;
    }
    this.errorMessage.set('');
    try {
      await firstValueFrom(this.api.marcarChatLeido(this.chatId()!));
      await this.cargarChat();
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo marcar el chat como leído.'));
    }
  }

  protected async cargarChat(): Promise<void> {
    if (!this.chatId()) {
      return;
    }
    try {
      const [mensajes, noLeidos] = await Promise.all([
        firstValueFrom(this.api.listMensajes(this.chatId()!)),
        firstValueFrom(this.api.contarNoLeidosChat(this.chatId()!)),
      ]);
      this.mensajes.set(mensajes.data ?? []);
      this.chatNoLeidos.set(noLeidos.data?.no_leidos ?? 0);
    } catch {
      this.mensajes.set([]);
      this.chatNoLeidos.set(0);
    }
  }

  private async loadAll(): Promise<void> {
    const ordenId = this.route.snapshot.paramMap.get('ordenId');
    if (!ordenId) {
      this.errorMessage.set('No se recibió un identificador de orden válido.');
      return;
    }

    this.errorMessage.set('');
    try {
      const [orden, asignaciones, presupuestos, mecanicos] = await Promise.all([
        firstValueFrom(this.api.getOrden(ordenId)),
        firstValueFrom(this.api.listAsignaciones(ordenId)),
        firstValueFrom(this.api.listPresupuestos(ordenId)),
        firstValueFrom(this.api.listMecanicos(true)),
      ]);
      this.orden.set(orden.data ?? null);
      this.asignaciones.set(asignaciones.data ?? []);
      this.presupuestos.set(presupuestos.data ?? []);
      this.mecanicos.set(mecanicos.data ?? []);

      if (!this.asignacionForm.value.mecanico_id && this.mecanicos().length) {
        this.asignacionForm.patchValue({ mecanico_id: this.mecanicos()[0].id });
      }

      await this.inicializarChat(ordenId);
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo cargar el detalle de la orden para taller.'));
    }
  }

  private async inicializarChat(ordenId: string): Promise<void> {
    try {
      const response = await firstValueFrom(this.api.getChatPorOrden(ordenId));
      this.chatId.set(response.data?.id ?? null);
      await this.cargarChat();
    } catch {
      this.chatId.set(null);
      this.mensajes.set([]);
      this.chatNoLeidos.set(0);
    }
  }
}
