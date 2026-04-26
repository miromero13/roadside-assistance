import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { firstValueFrom } from 'rxjs';

import { Averia, Vehiculo } from '../../../core/models/conductor.model';
import { ConductorApiService } from '../../../core/services/conductor-api.service';
import { getErrorMessage } from '../../../core/utils/http-error.util';

@Component({
  selector: 'app-conductor-averias-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <section class="space-y-5">
      <header>
        <h1 class="text-2xl font-semibold">Mis averías</h1>
        <p class="text-sm text-slate-500">Registra incidentes y adjunta enlaces de evidencias.</p>
      </header>

      <form class="grid gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4" [formGroup]="form" (ngSubmit)="createAveria()">
        <select class="rounded-lg border border-slate-300 px-3 py-2" formControlName="vehiculo_id">
          <option value="">Selecciona un vehículo</option>
          @for (vehiculo of vehiculos(); track vehiculo.id) {
            <option [value]="vehiculo.id">{{ vehiculo.placa }} - {{ vehiculo.marca }} {{ vehiculo.modelo }}</option>
          }
        </select>
        <textarea class="rounded-lg border border-slate-300 px-3 py-2" rows="3" placeholder="Descripción" formControlName="descripcion_conductor"></textarea>

        <div class="grid gap-3 sm:grid-cols-2">
          <input class="rounded-lg border border-slate-300 px-3 py-2" type="number" step="0.000001" placeholder="Latitud" formControlName="latitud_averia" />
          <input class="rounded-lg border border-slate-300 px-3 py-2" type="number" step="0.000001" placeholder="Longitud" formControlName="longitud_averia" />
        </div>

        <div class="grid gap-3 sm:grid-cols-2">
          <input class="rounded-lg border border-slate-300 px-3 py-2" placeholder="Dirección" formControlName="direccion_averia" />
          <select class="rounded-lg border border-slate-300 px-3 py-2" formControlName="prioridad">
            <option value="baja">Baja</option>
            <option value="media">Media</option>
            <option value="alta">Alta</option>
            <option value="critica">Crítica</option>
          </select>
        </div>

        <button class="w-fit rounded-lg bg-slate-900 px-4 py-2 text-sm text-white" type="submit" [disabled]="loading()">
          {{ loading() ? 'Registrando...' : 'Registrar avería' }}
        </button>
      </form>

      @if (errorMessage()) {
        <p class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ errorMessage() }}</p>
      }

      <div class="space-y-2">
        @for (averia of averias(); track averia.id) {
          <article class="space-y-3 rounded-xl border border-slate-200 p-3">
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="font-medium">{{ averia.descripcion_conductor }}</p>
                <p class="text-sm text-slate-500">Estado: {{ averia.estado }} · Prioridad: {{ averia.prioridad }}</p>
              </div>
              <span class="rounded-full bg-slate-100 px-2 py-1 text-xs">{{ averia.creado_en | date: 'short' }}</span>
            </div>

            <form class="flex flex-wrap gap-2" [formGroup]="medioForms[averia.id]" (ngSubmit)="addMedio(averia.id)">
              <select class="rounded-lg border border-slate-300 px-2 py-1 text-sm" formControlName="tipo">
                <option value="foto">Foto</option>
                <option value="video">Video</option>
                <option value="audio">Audio</option>
              </select>
              <input class="min-w-[280px] flex-1 rounded-lg border border-slate-300 px-2 py-1 text-sm" placeholder="URL evidencia" formControlName="url" />
              <button class="rounded-lg border border-slate-300 px-3 py-1 text-sm" type="submit">Adjuntar</button>
            </form>
          </article>
        }

        @if (!averias().length) {
          <p class="rounded-lg border border-dashed border-slate-300 px-3 py-4 text-sm text-slate-500">No tienes averías registradas.</p>
        }
      </div>
    </section>
  `,
})
export class ConductorAveriasPageComponent {
  private readonly fb = inject(FormBuilder);
  private readonly api = inject(ConductorApiService);

  protected readonly vehiculos = signal<Vehiculo[]>([]);
  protected readonly averias = signal<Averia[]>([]);
  protected readonly loading = signal(false);
  protected readonly errorMessage = signal('');
  protected readonly medioForms: Record<
    string,
    FormGroup<{
      tipo: FormControl<'foto' | 'video' | 'audio'>;
      url: FormControl<string>;
      orden_visualizacion: FormControl<number>;
    }>
  > = {};

  protected readonly form = this.fb.nonNullable.group({
    vehiculo_id: ['', Validators.required],
    descripcion_conductor: ['', Validators.required],
    latitud_averia: [-16.5, Validators.required],
    longitud_averia: [-68.15, Validators.required],
    direccion_averia: [''],
    prioridad: this.fb.nonNullable.control<'baja' | 'media' | 'alta' | 'critica'>('media'),
  });

  constructor() {
    void this.loadData();
  }

  protected async createAveria(): Promise<void> {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.loading.set(true);
    this.errorMessage.set('');
    try {
      await firstValueFrom(this.api.createAveria(this.form.getRawValue()));
      this.form.patchValue({ descripcion_conductor: '' });
      await this.loadAverias();
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo registrar la avería.'));
    } finally {
      this.loading.set(false);
    }
  }

  protected async addMedio(averiaId: string): Promise<void> {
    const form = this.medioForms[averiaId];
    if (!form || form.invalid) {
      return;
    }

    this.errorMessage.set('');
    try {
      await firstValueFrom(this.api.addAveriaMedio(averiaId, form.getRawValue()));
      form.patchValue({ url: '' });
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo adjuntar la evidencia.'));
    }
  }

  private async loadData(): Promise<void> {
    await Promise.all([this.loadVehiculos(), this.loadAverias()]);
  }

  private async loadVehiculos(): Promise<void> {
    try {
      const response = await firstValueFrom(this.api.listVehiculos());
      this.vehiculos.set(response.data ?? []);
      if (!this.form.value.vehiculo_id && this.vehiculos().length) {
        this.form.patchValue({ vehiculo_id: this.vehiculos()[0].id });
      }
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudieron cargar los vehículos.'));
    }
  }

  private async loadAverias(): Promise<void> {
    try {
      const response = await firstValueFrom(this.api.listAverias());
      const rows = response.data ?? [];
      this.averias.set(rows);
      for (const averia of rows) {
        if (!this.medioForms[averia.id]) {
          this.medioForms[averia.id] = this.fb.nonNullable.group({
            tipo: this.fb.nonNullable.control<'foto' | 'video' | 'audio'>('foto'),
            url: ['', Validators.required],
            orden_visualizacion: [1],
          });
        }
      }
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudieron cargar las averías.'));
    }
  }
}
