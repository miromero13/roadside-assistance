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
  templateUrl: './taller-perfil-page.component.html',
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
