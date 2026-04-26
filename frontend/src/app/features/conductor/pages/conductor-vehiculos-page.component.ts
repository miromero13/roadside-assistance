import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { firstValueFrom } from 'rxjs';

import { Vehiculo } from '../../../core/models/conductor.model';
import { ConductorApiService } from '../../../core/services/conductor-api.service';
import { getErrorMessage } from '../../../core/utils/http-error.util';

@Component({
  selector: 'app-conductor-vehiculos-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <section class="space-y-5">
      <header>
        <h1 class="text-2xl font-semibold">Mis vehículos</h1>
        <p class="text-sm text-slate-500">Registra y administra los vehículos vinculados a tu cuenta.</p>
      </header>

      <form class="grid gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4 sm:grid-cols-2" [formGroup]="form" (ngSubmit)="saveVehiculo()">
        <input class="rounded-lg border border-slate-300 px-3 py-2" placeholder="Marca" formControlName="marca" />
        <input class="rounded-lg border border-slate-300 px-3 py-2" placeholder="Modelo" formControlName="modelo" />
        <input class="rounded-lg border border-slate-300 px-3 py-2" placeholder="Año" type="number" formControlName="anio" />
        <input class="rounded-lg border border-slate-300 px-3 py-2" placeholder="Placa" formControlName="placa" />
        <input class="rounded-lg border border-slate-300 px-3 py-2" placeholder="Color" formControlName="color" />
        <select class="rounded-lg border border-slate-300 px-3 py-2" formControlName="tipo_combustible">
          <option value="gasolina">Gasolina</option>
          <option value="diesel">Diesel</option>
          <option value="electrico">Eléctrico</option>
          <option value="hibrido">Híbrido</option>
          <option value="gas">Gas</option>
        </select>

        <div class="sm:col-span-2 flex flex-wrap gap-2">
          <button class="rounded-lg bg-slate-900 px-4 py-2 text-sm text-white" type="submit" [disabled]="loading()">
            {{ editingId() ? 'Actualizar' : 'Agregar' }} vehículo
          </button>
          @if (editingId()) {
            <button class="rounded-lg border border-slate-300 px-4 py-2 text-sm" type="button" (click)="cancelEdit()">Cancelar</button>
          }
        </div>
      </form>

      @if (errorMessage()) {
        <p class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ errorMessage() }}</p>
      }

      <div class="space-y-2">
        @for (vehiculo of vehiculos(); track vehiculo.id) {
          <article class="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-200 p-3">
            <div>
              <p class="font-medium">{{ vehiculo.marca }} {{ vehiculo.modelo }} ({{ vehiculo.anio }})</p>
              <p class="text-sm text-slate-500">Placa {{ vehiculo.placa }} · {{ vehiculo.tipo_combustible }}</p>
            </div>
            <div class="flex gap-2">
              <button class="rounded-lg border border-slate-300 px-3 py-1 text-sm" type="button" (click)="startEdit(vehiculo)">Editar</button>
              <button class="rounded-lg border border-red-300 px-3 py-1 text-sm text-red-700" type="button" (click)="deleteVehiculo(vehiculo.id)">Eliminar</button>
            </div>
          </article>
        }

        @if (!vehiculos().length) {
          <p class="rounded-lg border border-dashed border-slate-300 px-3 py-4 text-sm text-slate-500">Aún no tienes vehículos registrados.</p>
        }
      </div>
    </section>
  `,
})
export class ConductorVehiculosPageComponent {
  private readonly fb = inject(FormBuilder);
  private readonly api = inject(ConductorApiService);

  protected readonly vehiculos = signal<Vehiculo[]>([]);
  protected readonly loading = signal(false);
  protected readonly errorMessage = signal('');
  protected readonly editingId = signal<string | null>(null);

  protected readonly form = this.fb.nonNullable.group({
    marca: ['', Validators.required],
    modelo: ['', Validators.required],
    anio: [2020, Validators.required],
    placa: ['', Validators.required],
    color: [''],
    tipo_combustible: this.fb.nonNullable.control<'gasolina' | 'diesel' | 'electrico' | 'hibrido' | 'gas'>('gasolina'),
  });

  constructor() {
    void this.loadVehiculos();
  }

  protected async saveVehiculo(): Promise<void> {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.loading.set(true);
    this.errorMessage.set('');
    try {
      const payload = this.form.getRawValue();
      if (this.editingId()) {
        await firstValueFrom(this.api.updateVehiculo(this.editingId()!, payload));
      } else {
        await firstValueFrom(this.api.createVehiculo(payload));
      }
      this.cancelEdit();
      await this.loadVehiculos();
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo guardar el vehículo.'));
    } finally {
      this.loading.set(false);
    }
  }

  protected startEdit(vehiculo: Vehiculo): void {
    this.editingId.set(vehiculo.id);
    this.form.patchValue({
      marca: vehiculo.marca,
      modelo: vehiculo.modelo,
      anio: vehiculo.anio,
      placa: vehiculo.placa,
      color: vehiculo.color ?? '',
      tipo_combustible: vehiculo.tipo_combustible,
    });
  }

  protected cancelEdit(): void {
    this.editingId.set(null);
    this.form.reset({
      marca: '',
      modelo: '',
      anio: 2020,
      placa: '',
      color: '',
      tipo_combustible: 'gasolina',
    });
  }

  protected async deleteVehiculo(vehiculoId: string): Promise<void> {
    this.errorMessage.set('');
    try {
      await firstValueFrom(this.api.deleteVehiculo(vehiculoId));
      await this.loadVehiculos();
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo eliminar el vehículo.'));
    }
  }

  private async loadVehiculos(): Promise<void> {
    try {
      const response = await firstValueFrom(this.api.listVehiculos());
      this.vehiculos.set(response.data ?? []);
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudieron cargar los vehículos.'));
    }
  }
}
