import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { firstValueFrom } from 'rxjs';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { lucideMoreVertical, lucidePlus, lucideX } from '@ng-icons/lucide';

import { Averia, Vehiculo } from '../../../core/models/conductor.model';
import { ConductorApiService } from '../../../core/services/conductor-api.service';
import { getErrorMessage } from '../../../core/utils/http-error.util';
import { HlmButton } from '../../../components/button/src';
import { HlmInput } from '../../../components/input/src';
import { HlmSelectImports } from '../../../components/select/src';
import { HlmTable } from '../../../components/table/src';
import { HlmTextarea } from '../../../components/textarea/src';

@Component({
  selector: 'app-conductor-averias-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, HlmButton, HlmInput, HlmTable, HlmTextarea, NgIcon, ...HlmSelectImports],
  providers: [provideIcons({ lucideMoreVertical, lucidePlus, lucideX })],
  templateUrl: './conductor-averias-page.component.html',
})
export class ConductorAveriasPageComponent {
  private readonly fb = inject(FormBuilder);
  private readonly api = inject(ConductorApiService);

  protected readonly vehiculos = signal<Vehiculo[]>([]);
  protected readonly averias = signal<Averia[]>([]);
  protected readonly loading = signal(false);
  protected readonly errorMessage = signal('');
  protected readonly averiaModalOpen = signal(false);
  protected readonly evidenciaModalAveriaId = signal<string | null>(null);
  protected readonly actionMenuOpenId = signal<string | null>(null);
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

  protected openAveriaModal(): void {
    this.actionMenuOpenId.set(null);
    this.form.patchValue({
      descripcion_conductor: '',
      direccion_averia: '',
      prioridad: 'media',
      latitud_averia: this.form.value.latitud_averia ?? -16.5,
      longitud_averia: this.form.value.longitud_averia ?? -68.15,
      vehiculo_id: this.form.value.vehiculo_id || this.vehiculos()[0]?.id || '',
    });
    this.averiaModalOpen.set(true);
  }

  protected closeAveriaModal(): void {
    this.averiaModalOpen.set(false);
  }

  protected openEvidenciaModal(averiaId: string): void {
    this.actionMenuOpenId.set(null);
    this.evidenciaModalAveriaId.set(averiaId);
    if (!this.medioForms[averiaId]) {
      this.medioForms[averiaId] = this.fb.nonNullable.group({
        tipo: this.fb.nonNullable.control<'foto' | 'video' | 'audio'>('foto'),
        url: ['', Validators.required],
        orden_visualizacion: [1],
      });
    }
  }

  protected closeEvidenciaModal(): void {
    this.evidenciaModalAveriaId.set(null);
  }

  protected toggleActionMenu(averiaId: string): void {
    this.actionMenuOpenId.set(this.actionMenuOpenId() === averiaId ? null : averiaId);
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
      this.closeAveriaModal();
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
      this.closeEvidenciaModal();
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
