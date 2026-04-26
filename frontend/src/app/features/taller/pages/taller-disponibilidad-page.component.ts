import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { firstValueFrom } from 'rxjs';

import { TallerBloqueo, TallerHorario } from '../../../core/models/taller.model';
import { TallerContextService } from '../../../core/services/taller-context.service';
import { TallerApiService } from '../../../core/services/taller-api.service';
import { getErrorMessage } from '../../../core/utils/http-error.util';

@Component({
  selector: 'app-taller-disponibilidad-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <section class="space-y-5">
      <header>
        <h1 class="text-2xl font-semibold">Disponibilidad</h1>
        <p class="text-sm text-slate-500">Gestiona horarios de atención y bloqueos temporales del taller.</p>
      </header>

      @if (loading()) {
        <p class="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-600">Cargando disponibilidad del taller...</p>
      }

      @if (errorMessage()) {
        <p class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ errorMessage() }}</p>
      }

      <section class="grid gap-4 lg:grid-cols-2">
        <article class="space-y-3 rounded-xl border border-slate-200 p-4">
          <h2 class="font-medium">Horarios</h2>
          <form class="grid gap-2" [formGroup]="horarioForm" (ngSubmit)="crearHorario()">
            <select class="rounded-lg border border-slate-300 px-3 py-2" formControlName="dia_semana">
              <option value="lunes">Lunes</option>
              <option value="martes">Martes</option>
              <option value="miercoles">Miércoles</option>
              <option value="jueves">Jueves</option>
              <option value="viernes">Viernes</option>
              <option value="sabado">Sábado</option>
              <option value="domingo">Domingo</option>
            </select>
            <div class="grid gap-2 sm:grid-cols-2">
              <input class="rounded-lg border border-slate-300 px-3 py-2" type="time" formControlName="hora_apertura" />
              <input class="rounded-lg border border-slate-300 px-3 py-2" type="time" formControlName="hora_cierre" />
            </div>
            <label class="flex items-center gap-2 text-sm">
              <input type="checkbox" formControlName="disponible" />
              Disponible
            </label>
            <button class="w-fit rounded-lg bg-slate-900 px-4 py-2 text-sm text-white" type="submit">Agregar horario</button>
          </form>

          <div class="space-y-2">
            @for (horario of horarios(); track horario.id) {
              <article class="flex items-center justify-between gap-2 rounded-lg bg-slate-50 p-2 text-sm">
                <div>
                  <p class="font-medium">{{ horario.dia_semana }} · {{ horario.hora_apertura }} - {{ horario.hora_cierre }}</p>
                  <p class="text-slate-500">Disponible: {{ horario.disponible ? 'Sí' : 'No' }}</p>
                </div>
                <button class="rounded-lg border border-red-300 px-2 py-1 text-red-700" type="button" (click)="eliminarHorario(horario.id)">Eliminar</button>
              </article>
            }
          </div>
        </article>

        <article class="space-y-3 rounded-xl border border-slate-200 p-4">
          <h2 class="font-medium">Bloqueos</h2>
          <form class="grid gap-2" [formGroup]="bloqueoForm" (ngSubmit)="crearBloqueo()">
            <div class="grid gap-2 sm:grid-cols-2">
              <label class="space-y-1 text-sm">
                <span>Inicio</span>
                <input class="w-full rounded-lg border border-slate-300 px-3 py-2" type="datetime-local" formControlName="fecha_inicio" />
              </label>
              <label class="space-y-1 text-sm">
                <span>Fin</span>
                <input class="w-full rounded-lg border border-slate-300 px-3 py-2" type="datetime-local" formControlName="fecha_fin" />
              </label>
            </div>
            <input class="rounded-lg border border-slate-300 px-3 py-2" placeholder="Motivo" formControlName="motivo" />
            <button class="w-fit rounded-lg bg-slate-900 px-4 py-2 text-sm text-white" type="submit">Agregar bloqueo</button>
          </form>

          <div class="space-y-2">
            @for (bloqueo of bloqueos(); track bloqueo.id) {
              <article class="flex items-center justify-between gap-2 rounded-lg bg-slate-50 p-2 text-sm">
                <div>
                  <p class="font-medium">{{ bloqueo.fecha_inicio | date: 'short' }} - {{ bloqueo.fecha_fin | date: 'short' }}</p>
                  <p class="text-slate-500">{{ bloqueo.motivo || 'Sin motivo' }}</p>
                </div>
                <button class="rounded-lg border border-red-300 px-2 py-1 text-red-700" type="button" (click)="eliminarBloqueo(bloqueo.id)">Eliminar</button>
              </article>
            }
          </div>
        </article>
      </section>
    </section>
  `,
})
export class TallerDisponibilidadPageComponent {
  private readonly api = inject(TallerApiService);
  private readonly ctx = inject(TallerContextService);
  private readonly fb = inject(FormBuilder);

  protected readonly horarios = signal<TallerHorario[]>([]);
  protected readonly bloqueos = signal<TallerBloqueo[]>([]);
  protected readonly errorMessage = signal('');
  protected readonly loading = signal(false);

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
