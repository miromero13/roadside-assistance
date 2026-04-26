import { CommonModule } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { firstValueFrom } from 'rxjs';

import {
  AsignacionOrden,
  Calificacion,
  Chat,
  Factura,
  HistorialEstadoOrden,
  MensajeChat,
  MetodoPago,
  Orden,
  Pago,
  Presupuesto,
} from '../../../core/models/conductor.model';
import { ConductorApiService } from '../../../core/services/conductor-api.service';
import { getErrorMessage } from '../../../core/utils/http-error.util';

@Component({
  selector: 'app-conductor-orden-detalle-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  template: `
    <section class="space-y-5">
      <a routerLink="/app/conductor/ordenes" class="text-sm text-slate-600 underline">← Volver a órdenes</a>

      <header class="space-y-1">
        <h1 class="text-2xl font-semibold">Detalle de orden</h1>
        @if (orden()) {
          <p class="text-sm text-slate-500">Estado actual: {{ orden()?.estado }} · Taller: {{ orden()?.taller_id }}</p>
        }
      </header>

      @if (errorMessage()) {
        <p class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ errorMessage() }}</p>
      }

      <section class="grid gap-4 lg:grid-cols-2">
        <article class="space-y-2 rounded-xl border border-slate-200 p-4">
          <h2 class="font-medium">Historial de estados</h2>
          @for (item of historial(); track item.id) {
            <div class="rounded-lg bg-slate-50 p-2 text-sm">
              <p class="font-medium">{{ item.estado_nuevo }}</p>
              <p class="text-slate-500">{{ item.creado_en | date: 'short' }}</p>
              @if (item.observacion) {
                <p class="text-slate-600">{{ item.observacion }}</p>
              }
            </div>
          }
          @if (!historial().length) {
            <p class="text-sm text-slate-500">Sin historial disponible.</p>
          }
        </article>

        <article class="space-y-2 rounded-xl border border-slate-200 p-4">
          <h2 class="font-medium">Asignaciones</h2>
          @for (asignacion of asignaciones(); track asignacion.id) {
            <div class="rounded-lg bg-slate-50 p-2 text-sm">
              <p class="font-medium">Mecánico: {{ asignacion.mecanico_id }}</p>
              <p class="text-slate-500">Estado: {{ asignacion.estado }} · {{ asignacion.asignado_en | date: 'short' }}</p>
            </div>
          }
          @if (!asignaciones().length) {
            <p class="text-sm text-slate-500">Aún no hay asignaciones en esta orden.</p>
          }
        </article>
      </section>

      <section class="space-y-3 rounded-xl border border-slate-200 p-4">
        <h2 class="font-medium">Presupuestos</h2>
        @for (presupuesto of presupuestos(); track presupuesto.id) {
          <article class="space-y-2 rounded-lg bg-slate-50 p-3">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <p class="font-medium">Versión {{ presupuesto.version }} · {{ presupuesto.estado }}</p>
              <p class="text-sm text-slate-500">Total: Bs {{ presupuesto.monto_total }}</p>
            </div>
            <p class="text-sm text-slate-600">{{ presupuesto.descripcion_trabajos }}</p>

            @if (presupuesto.estado === 'enviado') {
              <div class="flex flex-wrap gap-2">
                <button class="rounded-lg bg-emerald-700 px-3 py-1 text-sm text-white" type="button" (click)="aprobarPresupuesto(presupuesto.id)">
                  Aprobar
                </button>
                <button class="rounded-lg border border-red-300 px-3 py-1 text-sm text-red-700" type="button" (click)="setRechazoTarget(presupuesto.id)">
                  Rechazar
                </button>
                <button class="rounded-lg border border-slate-300 px-3 py-1 text-sm" type="button" (click)="preparePago(presupuesto.id, presupuesto.monto_total)">
                  Crear pago
                </button>
              </div>
            }

            @if (rechazoTargetId() === presupuesto.id) {
              <form class="mt-2 flex flex-wrap gap-2" [formGroup]="rechazoForm" (ngSubmit)="rechazarPresupuesto()">
                <input class="min-w-[240px] flex-1 rounded-lg border border-slate-300 px-2 py-1 text-sm" formControlName="motivo" placeholder="Motivo de rechazo" />
                <button class="rounded-lg bg-slate-900 px-3 py-1 text-sm text-white" type="submit">Confirmar</button>
                <button class="rounded-lg border border-slate-300 px-3 py-1 text-sm" type="button" (click)="clearRechazoTarget()">Cancelar</button>
              </form>
            }
          </article>
        }

        @if (!presupuestos().length) {
          <p class="text-sm text-slate-500">No hay presupuestos para esta orden.</p>
        }
      </section>

      @if (pagoTargetId()) {
        <section class="space-y-3 rounded-xl border border-slate-200 p-4">
          <h2 class="font-medium">Crear pago</h2>
          <form class="flex flex-wrap items-end gap-3" [formGroup]="pagoForm" (ngSubmit)="crearPago()">
            <label class="space-y-1 text-sm">
              <span>Método</span>
              <select class="rounded-lg border border-slate-300 px-3 py-2" formControlName="metodo">
                <option value="tarjeta">Tarjeta</option>
                <option value="qr">QR</option>
                <option value="efectivo">Efectivo</option>
              </select>
            </label>
            <label class="space-y-1 text-sm">
              <span>Monto</span>
              <input class="rounded-lg border border-slate-300 px-3 py-2" formControlName="monto" />
            </label>
            <button class="rounded-lg bg-slate-900 px-4 py-2 text-sm text-white" type="submit">Confirmar pago</button>
            <button class="rounded-lg border border-slate-300 px-4 py-2 text-sm" type="button" (click)="clearPagoTarget()">Cancelar</button>
          </form>
        </section>
      }

      @if (ultimoPago()) {
        <section class="space-y-2 rounded-xl border border-slate-200 p-4 text-sm">
          <h2 class="font-medium">Último pago creado</h2>
          <p>ID: {{ ultimoPago()?.id }}</p>
          <p>Estado: {{ ultimoPago()?.estado }} · Método: {{ ultimoPago()?.metodo }} · Monto Bs {{ ultimoPago()?.monto }}</p>
          <div class="flex flex-wrap gap-2">
            <button class="rounded-lg border border-slate-300 px-3 py-1" type="button" (click)="generarFacturaDesdePago()">
              Generar factura
            </button>
            <button class="rounded-lg border border-slate-300 px-3 py-1" type="button" (click)="recargarFacturaPorOrden()">
              Consultar factura de orden
            </button>
          </div>
        </section>
      }

      @if (factura()) {
        <section class="space-y-2 rounded-xl border border-slate-200 p-4 text-sm">
          <h2 class="font-medium">Factura</h2>
          <p>Número: {{ factura()?.numero_factura }}</p>
          <p>Total: Bs {{ factura()?.total }} · Emitida: {{ factura()?.emitida_en | date: 'short' }}</p>
          <p>Pago: {{ factura()?.pago_id }}</p>
        </section>
      }

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
            <input class="w-full rounded-lg border border-slate-300 px-3 py-2" placeholder="Escribe un mensaje" formControlName="contenido" />
          </label>
          <button class="rounded-lg bg-slate-900 px-4 py-2 text-sm text-white" type="submit">Enviar</button>
          <button class="rounded-lg border border-slate-300 px-4 py-2 text-sm" type="button" (click)="cargarChat()">Actualizar</button>
        </form>

        <div class="max-h-80 space-y-2 overflow-auto rounded-lg border border-slate-200 p-2">
          @for (mensaje of mensajes(); track mensaje.id) {
            <article class="rounded-lg bg-slate-50 p-2 text-sm">
              <div class="flex flex-wrap items-center justify-between gap-2">
                <p class="font-medium">{{ mensaje.remitente_id }}</p>
                <span class="text-xs text-slate-500">{{ mensaje.enviado_en | date: 'short' }}</span>
              </div>
              <p class="text-slate-700">{{ mensaje.contenido || '(sin contenido)' }}</p>
              <div class="mt-1 flex gap-2">
                <span class="rounded-full bg-slate-200 px-2 py-0.5 text-xs">{{ mensaje.tipo }}</span>
                @if (!mensaje.leido) {
                  <button class="rounded-lg border border-slate-300 px-2 py-0.5 text-xs" type="button" (click)="marcarMensajeLeido(mensaje.id)">
                    Marcar leído
                  </button>
                }
              </div>
            </article>
          }

          @if (!mensajes().length) {
            <p class="text-sm text-slate-500">No hay mensajes en este chat aún.</p>
          }
        </div>
      </section>

      <section class="space-y-3 rounded-xl border border-slate-200 p-4">
        <h2 class="font-medium">Calificación</h2>

        <form class="flex flex-wrap items-end gap-3" [formGroup]="calificacionForm" (ngSubmit)="enviarCalificacion()">
          <label class="space-y-1 text-sm">
            <span>Puntuación</span>
            <select class="rounded-lg border border-slate-300 px-3 py-2" formControlName="puntuacion">
              <option [value]="5">5</option>
              <option [value]="4">4</option>
              <option [value]="3">3</option>
              <option [value]="2">2</option>
              <option [value]="1">1</option>
            </select>
          </label>
          <label class="space-y-1 text-sm min-w-[280px] flex-1">
            <span>Comentario</span>
            <input class="w-full rounded-lg border border-slate-300 px-3 py-2" formControlName="comentario" placeholder="¿Cómo fue el servicio?" />
          </label>
          <button class="rounded-lg bg-slate-900 px-4 py-2 text-sm text-white" type="submit">Enviar</button>
        </form>

        @for (calificacion of calificaciones(); track calificacion.id) {
          <article class="rounded-lg bg-slate-50 p-3 text-sm">
            <p class="font-medium">{{ calificacion.puntuacion }}/5</p>
            <p class="text-slate-500">{{ calificacion.creado_en | date: 'short' }}</p>
            @if (calificacion.comentario) {
              <p class="text-slate-700">{{ calificacion.comentario }}</p>
            }
          </article>
        }

        @if (!calificaciones().length) {
          <p class="text-sm text-slate-500">Aún no hay calificaciones registradas para esta orden.</p>
        }
      </section>
    </section>
  `,
})
export class ConductorOrdenDetallePageComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly api = inject(ConductorApiService);
  private readonly fb = inject(FormBuilder);

  protected readonly orden = signal<Orden | null>(null);
  protected readonly historial = signal<HistorialEstadoOrden[]>([]);
  protected readonly asignaciones = signal<AsignacionOrden[]>([]);
  protected readonly presupuestos = signal<Presupuesto[]>([]);
  protected readonly ultimoPago = signal<Pago | null>(null);
  protected readonly factura = signal<Factura | null>(null);
  protected readonly calificaciones = signal<Calificacion[]>([]);
  protected readonly chat = signal<Chat | null>(null);
  protected readonly mensajes = signal<MensajeChat[]>([]);
  protected readonly chatNoLeidos = signal(0);
  protected readonly errorMessage = signal('');

  protected readonly rechazoTargetId = signal<string | null>(null);
  protected readonly pagoTargetId = signal<string | null>(null);
  protected readonly rechazoForm = this.fb.nonNullable.group({
    motivo: ['', [Validators.required, Validators.minLength(3)]],
  });
  protected readonly pagoForm = this.fb.nonNullable.group({
    metodo: this.fb.nonNullable.control<MetodoPago>('tarjeta'),
    monto: ['', [Validators.required]],
  });
  protected readonly calificacionForm = this.fb.nonNullable.group({
    puntuacion: [5, [Validators.required]],
    comentario: [''],
  });
  protected readonly chatForm = this.fb.nonNullable.group({
    contenido: ['', [Validators.required, Validators.minLength(1)]],
  });

  private readonly ordenId = computed(() => this.route.snapshot.paramMap.get('ordenId') ?? '');

  constructor() {
    void this.loadAll();
  }

  protected async aprobarPresupuesto(presupuestoId: string): Promise<void> {
    this.errorMessage.set('');
    try {
      await firstValueFrom(this.api.aprobarPresupuesto(presupuestoId));
      await this.loadAll();
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo aprobar el presupuesto.'));
    }
  }

  protected setRechazoTarget(presupuestoId: string): void {
    this.rechazoTargetId.set(presupuestoId);
    this.rechazoForm.reset({ motivo: '' });
  }

  protected clearRechazoTarget(): void {
    this.rechazoTargetId.set(null);
    this.rechazoForm.reset({ motivo: '' });
  }

  protected async rechazarPresupuesto(): Promise<void> {
    if (this.rechazoForm.invalid || !this.rechazoTargetId()) {
      this.rechazoForm.markAllAsTouched();
      return;
    }
    this.errorMessage.set('');
    try {
      await firstValueFrom(
        this.api.rechazarPresupuesto(this.rechazoTargetId()!, this.rechazoForm.getRawValue().motivo),
      );
      this.clearRechazoTarget();
      await this.loadAll();
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo rechazar el presupuesto.'));
    }
  }

  protected preparePago(presupuestoId: string, montoTotal: string): void {
    this.pagoTargetId.set(presupuestoId);
    this.pagoForm.reset({ metodo: 'tarjeta', monto: montoTotal });
  }

  protected clearPagoTarget(): void {
    this.pagoTargetId.set(null);
    this.pagoForm.reset({ metodo: 'tarjeta', monto: '' });
  }

  protected async crearPago(): Promise<void> {
    const ordenId = this.ordenId();
    const presupuestoId = this.pagoTargetId();
    if (!ordenId || !presupuestoId || this.pagoForm.invalid) {
      this.pagoForm.markAllAsTouched();
      return;
    }
    this.errorMessage.set('');
    try {
      const payload = this.pagoForm.getRawValue();
      const response = await firstValueFrom(this.api.crearPago(ordenId, presupuestoId, payload.metodo, payload.monto));
      this.ultimoPago.set(response.data ?? null);
      this.clearPagoTarget();
      await this.loadAll();
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo crear el pago.'));
    }
  }

  protected async generarFacturaDesdePago(): Promise<void> {
    const pago = this.ultimoPago();
    if (!pago) {
      return;
    }
    this.errorMessage.set('');
    try {
      const response = await firstValueFrom(this.api.generarFacturaPorPago(pago.id));
      this.factura.set(response.data ?? null);
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo generar la factura para este pago.'));
    }
  }

  protected async recargarFacturaPorOrden(): Promise<void> {
    const ordenId = this.ordenId();
    if (!ordenId) {
      return;
    }
    this.errorMessage.set('');
    try {
      const response = await firstValueFrom(this.api.getFacturaPorOrden(ordenId));
      this.factura.set(response.data ?? null);
    } catch {
      this.factura.set(null);
    }
  }

  protected async enviarCalificacion(): Promise<void> {
    const ordenId = this.ordenId();
    if (!ordenId || this.calificacionForm.invalid) {
      this.calificacionForm.markAllAsTouched();
      return;
    }

    this.errorMessage.set('');
    try {
      const payload = this.calificacionForm.getRawValue();
      await firstValueFrom(this.api.crearCalificacion(ordenId, payload.puntuacion, payload.comentario));
      await this.cargarCalificaciones(ordenId);
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo registrar la calificación.'));
    }
  }

  protected async enviarMensajeChat(): Promise<void> {
    if (this.chatForm.invalid) {
      this.chatForm.markAllAsTouched();
      return;
    }

    const chatId = this.chat()?.id;
    if (!chatId) {
      return;
    }

    this.errorMessage.set('');
    try {
      const { contenido } = this.chatForm.getRawValue();
      await firstValueFrom(this.api.enviarMensaje(chatId, contenido));
      this.chatForm.reset({ contenido: '' });
      await this.cargarChat();
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo enviar el mensaje.'));
    }
  }

  protected async marcarMensajeLeido(mensajeId: string): Promise<void> {
    const chatId = this.chat()?.id;
    if (!chatId) {
      return;
    }
    this.errorMessage.set('');
    try {
      await firstValueFrom(this.api.marcarMensajeLeido(chatId, mensajeId));
      await this.cargarChat();
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo marcar el mensaje como leído.'));
    }
  }

  protected async marcarChatLeido(): Promise<void> {
    const chatId = this.chat()?.id;
    if (!chatId) {
      return;
    }
    this.errorMessage.set('');
    try {
      await firstValueFrom(this.api.marcarChatLeido(chatId));
      await this.cargarChat();
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo marcar el chat como leído.'));
    }
  }

  protected async cargarChat(): Promise<void> {
    const chatId = this.chat()?.id;
    if (!chatId) {
      return;
    }
    try {
      const [mensajes, noLeidos] = await Promise.all([
        firstValueFrom(this.api.listMensajes(chatId)),
        firstValueFrom(this.api.contarNoLeidosChat(chatId)),
      ]);
      this.mensajes.set(mensajes.data ?? []);
      this.chatNoLeidos.set(noLeidos.data?.no_leidos ?? 0);
    } catch {
      this.mensajes.set([]);
      this.chatNoLeidos.set(0);
    }
  }

  private async loadAll(): Promise<void> {
    const ordenId = this.ordenId();
    if (!ordenId) {
      this.errorMessage.set('No se recibió un identificador de orden válido.');
      return;
    }

    this.errorMessage.set('');
    try {
      const [orden, historial, asignaciones, presupuestos] = await Promise.all([
        firstValueFrom(this.api.getOrden(ordenId)),
        firstValueFrom(this.api.getOrdenHistorial(ordenId)),
        firstValueFrom(this.api.getOrdenAsignaciones(ordenId)),
        firstValueFrom(this.api.getOrdenPresupuestos(ordenId)),
      ]);

      this.orden.set(orden.data ?? null);
      this.historial.set(historial.data ?? []);
      this.asignaciones.set(asignaciones.data ?? []);
      this.presupuestos.set(presupuestos.data ?? []);
      await Promise.all([
        this.recargarFacturaPorOrden(),
        this.cargarCalificaciones(ordenId),
        this.inicializarChat(ordenId),
      ]);
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo cargar el detalle de la orden.'));
    }
  }

  private async cargarCalificaciones(ordenId: string): Promise<void> {
    try {
      const response = await firstValueFrom(this.api.listCalificaciones(ordenId));
      this.calificaciones.set(response.data ?? []);
    } catch {
      this.calificaciones.set([]);
    }
  }

  private async inicializarChat(ordenId: string): Promise<void> {
    try {
      const response = await firstValueFrom(this.api.getChatPorOrden(ordenId));
      this.chat.set(response.data ?? null);
      await this.cargarChat();
    } catch {
      this.chat.set(null);
      this.mensajes.set([]);
      this.chatNoLeidos.set(0);
    }
  }
}
