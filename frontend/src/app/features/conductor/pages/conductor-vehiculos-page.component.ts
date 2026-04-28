import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { firstValueFrom } from 'rxjs';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { lucideMoreVertical, lucidePlus, lucideX } from '@ng-icons/lucide';

import { Vehiculo } from '../../../core/models/conductor.model';
import { ConductorApiService } from '../../../core/services/conductor-api.service';
import { getErrorMessage } from '../../../core/utils/http-error.util';
import { HlmButton } from '../../../components/button/src';
import { HlmInput } from '../../../components/input/src';
import { HlmSelectImports } from '../../../components/select/src';
import { HlmTable } from '../../../components/table/src';

@Component({
  selector: 'app-conductor-vehiculos-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, HlmButton, HlmInput, HlmTable, NgIcon, ...HlmSelectImports],
  providers: [provideIcons({ lucideMoreVertical, lucidePlus, lucideX })],
  templateUrl: './conductor-vehiculos-page.component.html',
})
export class ConductorVehiculosPageComponent {
  private readonly fb = inject(FormBuilder);
  private readonly api = inject(ConductorApiService);

  protected readonly vehiculos = signal<Vehiculo[]>([]);
  protected readonly loading = signal(false);
  protected readonly errorMessage = signal('');
  protected readonly editingId = signal<string | null>(null);
  protected readonly modalOpen = signal(false);
  protected readonly actionMenuOpenId = signal<string | null>(null);

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

  protected openCreateModal(): void {
    this.editingId.set(null);
    this.actionMenuOpenId.set(null);
    this.form.reset({
      marca: '',
      modelo: '',
      anio: 2020,
      placa: '',
      color: '',
      tipo_combustible: 'gasolina',
    });
    this.modalOpen.set(true);
  }

  protected closeModal(): void {
    this.modalOpen.set(false);
    this.editingId.set(null);
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
      this.closeModal();
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
    this.actionMenuOpenId.set(null);
    this.modalOpen.set(true);
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

  protected toggleActionMenu(vehiculoId: string): void {
    this.actionMenuOpenId.set(this.actionMenuOpenId() === vehiculoId ? null : vehiculoId);
  }

  protected async deleteVehiculo(vehiculoId: string): Promise<void> {
    this.actionMenuOpenId.set(null);
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
