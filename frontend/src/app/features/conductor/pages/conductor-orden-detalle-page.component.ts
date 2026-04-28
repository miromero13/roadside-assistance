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
  templateUrl: './conductor-orden-detalle-page.component.html',
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
