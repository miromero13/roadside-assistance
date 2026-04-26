import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { firstValueFrom } from 'rxjs';

import { TallerServicio } from '../../../core/models/taller.model';
import { TallerContextService } from '../../../core/services/taller-context.service';
import { TallerApiService } from '../../../core/services/taller-api.service';
import { getErrorMessage } from '../../../core/utils/http-error.util';

@Component({
  selector: 'app-taller-servicios-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <section class="space-y-5">
      <header>
        <h1 class="text-2xl font-semibold">Servicios del taller</h1>
        <p class="text-sm text-slate-500">Administra el catálogo de servicios que ofrece tu taller.</p>
      </header>

      @if (loading()) {
        <p class="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-600">Cargando datos del taller...</p>
      }

      <form class="grid gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4 sm:grid-cols-2" [formGroup]="form" (ngSubmit)="crearServicio()">
        <select class="rounded-lg border border-slate-300 px-3 py-2" formControlName="categoria_id">
          <option value="">Selecciona categoría</option>
          @for (categoria of categorias(); track categoria.id) {
            <option [value]="categoria.id">{{ categoria.nombre }}</option>
          }
        </select>
        <input class="rounded-lg border border-slate-300 px-3 py-2" placeholder="Descripción" formControlName="descripcion" />
        <input class="rounded-lg border border-slate-300 px-3 py-2" type="number" placeholder="Precio min" formControlName="precio_base_min" />
        <input class="rounded-lg border border-slate-300 px-3 py-2" type="number" placeholder="Precio max" formControlName="precio_base_max" />
        <input class="rounded-lg border border-slate-300 px-3 py-2" type="number" placeholder="Tiempo estimado (min)" formControlName="tiempo_estimado_min" />
        <label class="flex items-center gap-2 text-sm">
          <input type="checkbox" formControlName="servicio_movil" />
          Servicio móvil
        </label>
        <div class="sm:col-span-2">
          <button class="rounded-lg bg-slate-900 px-4 py-2 text-sm text-white" type="submit">Crear servicio</button>
        </div>
      </form>

      @if (errorMessage()) {
        <p class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ errorMessage() }}</p>
      }

      <div class="space-y-2">
        @for (servicio of servicios(); track servicio.id) {
          <article class="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-200 p-3">
            <div class="text-sm">
              <p class="font-medium">{{ servicio.descripcion || 'Sin descripción' }}</p>
              <p class="text-slate-500">Categoría: {{ servicio.categoria_id }} · Activo: {{ servicio.activo ? 'Sí' : 'No' }}</p>
              <p class="text-slate-700">Bs {{ servicio.precio_base_min || '-' }} - {{ servicio.precio_base_max || '-' }}</p>
            </div>
            <button class="rounded-lg border border-red-300 px-3 py-1 text-sm text-red-700" type="button" (click)="eliminarServicio(servicio.id)">
              Desactivar
            </button>
          </article>
        }

        @if (!servicios().length) {
          <p class="rounded-lg border border-dashed border-slate-300 px-3 py-4 text-sm text-slate-500">No hay servicios creados en tu taller.</p>
        }
      </div>
    </section>
  `,
})
export class TallerServiciosPageComponent {
  private readonly api = inject(TallerApiService);
  private readonly ctx = inject(TallerContextService);
  private readonly fb = inject(FormBuilder);

  protected readonly categorias = signal<Array<{ id: string; nombre: string }>>([]);
  protected readonly servicios = signal<TallerServicio[]>([]);
  protected readonly errorMessage = signal('');
  protected readonly loading = signal(false);

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
