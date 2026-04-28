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
  templateUrl: './taller-orden-detalle-page.component.html',
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
