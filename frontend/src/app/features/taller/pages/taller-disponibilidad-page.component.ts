import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { firstValueFrom } from 'rxjs';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { lucideMoreVertical, lucidePlus, lucideX } from '@ng-icons/lucide';

import { TallerBloqueo, TallerHorario } from '../../../core/models/taller.model';
import { TallerContextService } from '../../../core/services/taller-context.service';
import { TallerApiService } from '../../../core/services/taller-api.service';
import { getErrorMessage } from '../../../core/utils/http-error.util';
import { HlmButton } from '../../../components/button/src';
import { HlmInput } from '../../../components/input/src';
import { HlmSelectImports } from '../../../components/select/src';
import { HlmTable } from '../../../components/table/src';

@Component({
  selector: 'app-taller-disponibilidad-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, HlmButton, HlmInput, HlmTable, NgIcon, ...HlmSelectImports],
  providers: [provideIcons({ lucideMoreVertical, lucidePlus, lucideX })],
  templateUrl: './taller-disponibilidad-page.component.html',
})
export class TallerDisponibilidadPageComponent {
  private readonly api = inject(TallerApiService);
  private readonly ctx = inject(TallerContextService);
  private readonly fb = inject(FormBuilder);

  protected readonly horarios = signal<TallerHorario[]>([]);
  protected readonly bloqueos = signal<TallerBloqueo[]>([]);
  protected readonly errorMessage = signal('');
  protected readonly loading = signal(false);
  protected readonly horarioModalOpen = signal(false);
  protected readonly bloqueoModalOpen = signal(false);
  protected readonly horarioActionMenuOpenId = signal<string | null>(null);
  protected readonly bloqueoActionMenuOpenId = signal<string | null>(null);

  protected readonly horarioForm = this.fb.nonNullable.group({
    dia_semana: this.fb.nonNullable.control('lunes'),
    hora_apertura: ['08:00', Validators.required],
    hora_cierre: ['18:00', Validators.required],
    disponible: [true],
  });

  protected readonly bloqueoForm = this.fb.nonNullable.group({
    fecha_inicio: ['', Validators.required],
    fecha_fin: ['', Validators.required],
    motivo: [''],
  });

  constructor() {
    void this.resolveAndLoad();
  }

  protected openHorarioModal(): void {
    this.horarioActionMenuOpenId.set(null);
    this.horarioForm.reset({
      dia_semana: 'lunes',
      hora_apertura: '08:00',
      hora_cierre: '18:00',
      disponible: true,
    });
    this.horarioModalOpen.set(true);
  }

  protected closeHorarioModal(): void {
    this.horarioModalOpen.set(false);
  }

  protected openBloqueoModal(): void {
    this.bloqueoActionMenuOpenId.set(null);
    this.bloqueoForm.reset({ fecha_inicio: '', fecha_fin: '', motivo: '' });
    this.bloqueoModalOpen.set(true);
  }

  protected closeBloqueoModal(): void {
    this.bloqueoModalOpen.set(false);
  }

  protected toggleHorarioActionMenu(horarioId: string): void {
    this.horarioActionMenuOpenId.set(this.horarioActionMenuOpenId() === horarioId ? null : horarioId);
  }

  protected toggleBloqueoActionMenu(bloqueoId: string): void {
    this.bloqueoActionMenuOpenId.set(this.bloqueoActionMenuOpenId() === bloqueoId ? null : bloqueoId);
  }

  protected async crearHorario(): Promise<void> {
    const tallerId = await this.ensureTallerId();
    if (!tallerId) {
      this.errorMessage.set('No se encontró taller asociado al usuario.');
      return;
    }
    if (this.horarioForm.invalid) {
      this.horarioForm.markAllAsTouched();
      return;
    }
    this.errorMessage.set('');
    try {
      const raw = this.horarioForm.getRawValue();
      await firstValueFrom(this.api.createHorario(tallerId, raw));
      this.closeHorarioModal();
      await this.cargarDisponibilidad(tallerId);
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo crear el horario.'));
    }
  }

  protected async eliminarHorario(horarioId: string): Promise<void> {
    const tallerId = await this.ensureTallerId();
    if (!tallerId) {
      return;
    }
    this.errorMessage.set('');
    try {
      await firstValueFrom(this.api.deleteHorario(tallerId, horarioId));
      this.horarioActionMenuOpenId.set(null);
      await this.cargarDisponibilidad(tallerId);
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo eliminar el horario.'));
    }
  }

  protected async crearBloqueo(): Promise<void> {
    const tallerId = await this.ensureTallerId();
    if (!tallerId) {
      this.errorMessage.set('No se encontró taller asociado al usuario.');
      return;
    }
    if (this.bloqueoForm.invalid) {
      this.bloqueoForm.markAllAsTouched();
      return;
    }
    this.errorMessage.set('');
    try {
      const raw = this.bloqueoForm.getRawValue();
      await firstValueFrom(
        this.api.createBloqueo(tallerId, {
          fecha_inicio: new Date(raw.fecha_inicio).toISOString(),
          fecha_fin: new Date(raw.fecha_fin).toISOString(),
          motivo: raw.motivo,
        }),
      );
      this.closeBloqueoModal();
      await this.cargarDisponibilidad(tallerId);
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo crear el bloqueo.'));
    }
  }

  protected async eliminarBloqueo(bloqueoId: string): Promise<void> {
    const tallerId = await this.ensureTallerId();
    if (!tallerId) {
      return;
    }
    this.errorMessage.set('');
    try {
      await firstValueFrom(this.api.deleteBloqueo(tallerId, bloqueoId));
      this.bloqueoActionMenuOpenId.set(null);
      await this.cargarDisponibilidad(tallerId);
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo eliminar el bloqueo.'));
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
      await this.cargarDisponibilidad(tallerId);
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

  private async cargarDisponibilidad(tallerId: string): Promise<void> {
    this.errorMessage.set('');
    try {
      const [horarios, bloqueos] = await Promise.all([
        firstValueFrom(this.api.listHorarios(tallerId)),
        firstValueFrom(this.api.listBloqueos(tallerId)),
      ]);
      this.horarios.set(horarios.data ?? []);
      this.bloqueos.set(bloqueos.data ?? []);
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo cargar la disponibilidad del taller.'));
    }
  }
}
