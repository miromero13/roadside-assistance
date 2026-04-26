import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { firstValueFrom } from 'rxjs';

import { TallerContextService } from '../../../core/services/taller-context.service';
import { TallerApiService } from '../../../core/services/taller-api.service';
import { getErrorMessage } from '../../../core/utils/http-error.util';

@Component({
  selector: 'app-taller-perfil-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <section class="space-y-5">
      <header>
        <h1 class="text-2xl font-semibold">Perfil del taller</h1>
        <p class="text-sm text-slate-500">Configura datos base de tu taller para operar en la plataforma.</p>
      </header>

      @if (loading()) {
        <p class="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-600">Cargando taller...</p>
      }

      @if (tallerId()) {
        <p class="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-600">Taller activo: <span class="font-mono">{{ tallerId() }}</span></p>
      }

      <form class="grid gap-3 rounded-xl border border-slate-200 p-4 sm:grid-cols-2" [formGroup]="perfilForm" (ngSubmit)="guardarPerfil()">
        <input class="rounded-lg border border-slate-300 px-3 py-2" placeholder="Nombre" formControlName="nombre" />
        <input class="rounded-lg border border-slate-300 px-3 py-2" placeholder="Teléfono" formControlName="telefono" />
        <input class="sm:col-span-2 rounded-lg border border-slate-300 px-3 py-2" placeholder="Dirección" formControlName="direccion" />
        <input class="rounded-lg border border-slate-300 px-3 py-2" type="number" step="0.000001" placeholder="Latitud" formControlName="latitud" />
        <input class="rounded-lg border border-slate-300 px-3 py-2" type="number" step="0.000001" placeholder="Longitud" formControlName="longitud" />
        <input class="rounded-lg border border-slate-300 px-3 py-2" type="number" step="0.1" placeholder="Radio cobertura km" formControlName="radio_cobertura_km" />
        <input class="rounded-lg border border-slate-300 px-3 py-2" placeholder="Foto URL" formControlName="foto_url" />
        <label class="sm:col-span-2 flex items-center gap-2 text-sm">
          <input type="checkbox" formControlName="acepta_domicilio" />
          Acepta servicio a domicilio
        </label>
        <textarea class="sm:col-span-2 rounded-lg border border-slate-300 px-3 py-2" rows="2" placeholder="Descripción" formControlName="descripcion"></textarea>

        <div class="sm:col-span-2">
          <button class="rounded-lg bg-slate-900 px-4 py-2 text-sm text-white" type="submit">Guardar cambios</button>
        </div>
      </form>

      @if (errorMessage()) {
        <p class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ errorMessage() }}</p>
      }
      @if (successMessage()) {
        <p class="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">{{ successMessage() }}</p>
      }
    </section>
  `,
})
export class TallerPerfilPageComponent {
  private readonly api = inject(TallerApiService);
  private readonly ctx = inject(TallerContextService);
  private readonly fb = inject(FormBuilder);

  protected readonly errorMessage = signal('');
  protected readonly successMessage = signal('');
  protected readonly loading = signal(false);
  protected readonly tallerId = signal<string | null>(this.ctx.tallerId());

  protected readonly perfilForm = this.fb.nonNullable.group({
    nombre: [''],
    descripcion: [''],
    direccion: [''],
    latitud: [-16.5],
    longitud: [-68.15],
    radio_cobertura_km: [10],
    telefono: [''],
    foto_url: [''],
    acepta_domicilio: [true],
  });

  constructor() {
    void this.resolveAndLoad();
  }

  protected async guardarPerfil(): Promise<void> {
    const currentTallerId = this.tallerId();
    if (!currentTallerId) {
      this.errorMessage.set('No se encontró taller asociado al usuario.');
      return;
    }

    this.errorMessage.set('');
    this.successMessage.set('');
    this.loading.set(true);
    try {
      await firstValueFrom(this.api.updateTaller(currentTallerId, this.perfilForm.getRawValue()));
      this.successMessage.set('Perfil de taller actualizado correctamente.');
      await this.loadPerfil();
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo actualizar el perfil del taller.'));
    } finally {
      this.loading.set(false);
    }
  }

  private async resolveAndLoad(): Promise<void> {
    this.loading.set(true);
    this.errorMessage.set('');
    try {
      const response = await firstValueFrom(this.api.getMiTaller());
      const taller = response.data;
      if (!taller) {
        this.errorMessage.set('No se encontró taller asociado al usuario.');
        return;
      }
      this.ctx.setTallerId(taller.id);
      this.tallerId.set(taller.id);
      this.perfilForm.patchValue({
        nombre: taller.nombre,
        descripcion: taller.descripcion ?? '',
        direccion: taller.direccion,
        latitud: taller.latitud,
        longitud: taller.longitud,
        radio_cobertura_km: taller.radio_cobertura_km,
        telefono: taller.telefono,
        foto_url: taller.foto_url ?? '',
        acepta_domicilio: taller.acepta_domicilio,
      });
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo resolver el taller del usuario.'));
    } finally {
      this.loading.set(false);
    }
  }

  private async loadPerfil(): Promise<void> {
    const currentTallerId = this.tallerId();
    if (!currentTallerId) {
      return;
    }
    this.errorMessage.set('');
    this.loading.set(true);
    try {
      const response = await firstValueFrom(this.api.getTaller(currentTallerId));
      const taller = response.data;
      if (!taller) {
        return;
      }
      this.perfilForm.patchValue({
        nombre: taller.nombre,
        descripcion: taller.descripcion ?? '',
        direccion: taller.direccion,
        latitud: taller.latitud,
        longitud: taller.longitud,
        radio_cobertura_km: taller.radio_cobertura_km,
        telefono: taller.telefono,
        foto_url: taller.foto_url ?? '',
        acepta_domicilio: taller.acepta_domicilio,
      });
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo cargar el perfil del taller.'));
    } finally {
      this.loading.set(false);
    }
  }
}
