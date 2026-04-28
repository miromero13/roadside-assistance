import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { firstValueFrom } from 'rxjs';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { lucideMoreVertical, lucidePlus, lucideX } from '@ng-icons/lucide';

import { TallerServicio } from '../../../core/models/taller.model';
import { TallerContextService } from '../../../core/services/taller-context.service';
import { TallerApiService } from '../../../core/services/taller-api.service';
import { getErrorMessage } from '../../../core/utils/http-error.util';
import { HlmButton } from '../../../components/button/src';
import { HlmInput } from '../../../components/input/src';
import { HlmSelectImports } from '../../../components/select/src';
import { HlmTable } from '../../../components/table/src';

@Component({
  selector: 'app-taller-servicios-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, HlmButton, HlmInput, HlmTable, NgIcon, ...HlmSelectImports],
  providers: [provideIcons({ lucideMoreVertical, lucidePlus, lucideX })],
  templateUrl: './taller-servicios-page.component.html',
})
export class TallerServiciosPageComponent {
  private readonly api = inject(TallerApiService);
  private readonly ctx = inject(TallerContextService);
  private readonly fb = inject(FormBuilder);

  protected readonly categorias = signal<Array<{ id: string; nombre: string }>>([]);
  protected readonly servicios = signal<TallerServicio[]>([]);
  protected readonly errorMessage = signal('');
  protected readonly loading = signal(false);
  protected readonly modalOpen = signal(false);
  protected readonly actionMenuOpenId = signal<string | null>(null);

  protected readonly form = this.fb.nonNullable.group({
    categoria_id: ['', Validators.required],
    descripcion: [''],
    precio_base_min: [0],
    precio_base_max: [0],
    tiempo_estimado_min: [30],
    servicio_movil: [true],
  });

  constructor() {
    void this.resolveAndLoad();
  }

  protected openCreateModal(): void {
    this.actionMenuOpenId.set(null);
    this.form.reset({
      categoria_id: '',
      descripcion: '',
      precio_base_min: 0,
      precio_base_max: 0,
      tiempo_estimado_min: 30,
      servicio_movil: true,
    });
    this.modalOpen.set(true);
  }

  protected closeModal(): void {
    this.modalOpen.set(false);
  }

  protected toggleActionMenu(servicioId: string): void {
    this.actionMenuOpenId.set(this.actionMenuOpenId() === servicioId ? null : servicioId);
  }

  protected async crearServicio(): Promise<void> {
    const tallerId = await this.ensureTallerId();
    if (!tallerId) {
      this.errorMessage.set('No se encontró taller asociado al usuario.');
      return;
    }
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.errorMessage.set('');
    try {
      await firstValueFrom(this.api.createServicio(tallerId, this.form.getRawValue()));
      this.closeModal();
      await this.cargarServicios(tallerId);
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo crear el servicio.'));
    }
  }

  protected async eliminarServicio(servicioId: string): Promise<void> {
    const tallerId = await this.ensureTallerId();
    if (!tallerId) {
      return;
    }
    this.errorMessage.set('');
    try {
      await firstValueFrom(this.api.deleteServicio(servicioId));
      this.actionMenuOpenId.set(null);
      await this.cargarServicios(tallerId);
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo desactivar el servicio.'));
    }
  }

  private async resolveAndLoad(): Promise<void> {
    this.loading.set(true);
    const tallerId = await this.ensureTallerId();
    if (!tallerId) {
      this.errorMessage.set('No se encontró taller asociado al usuario.');
      this.loading.set(false);
      return;
    }

    try {
      await Promise.all([this.cargarCategorias(), this.cargarServicios(tallerId)]);
    } finally {
      this.loading.set(false);
    }
  }

  private async ensureTallerId(): Promise<string | null> {
    const currentTallerId = this.ctx.tallerId();
    if (currentTallerId) {
      return currentTallerId;
    }

    try {
      const response = await firstValueFrom(this.api.getMiTaller());
      const tallerId = response.data?.id ?? null;
      if (tallerId) {
        this.ctx.setTallerId(tallerId);
      }
      return tallerId;
    } catch {
      return null;
    }
  }

  private async cargarCategorias(): Promise<void> {
    const response = await firstValueFrom(this.api.listCategorias());
    this.categorias.set((response.data ?? []).map((c) => ({ id: c.id, nombre: c.nombre })));
  }

  private async cargarServicios(tallerId: string): Promise<void> {
    const response = await firstValueFrom(this.api.listServicios(tallerId));
    this.servicios.set(response.data ?? []);
  }
}
