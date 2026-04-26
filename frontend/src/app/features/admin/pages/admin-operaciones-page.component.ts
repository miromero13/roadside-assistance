import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { firstValueFrom } from 'rxjs';

import { AdminMecanico, AdminUsuario } from '../../../core/models/admin.model';
import { AdminApiService } from '../../../core/services/admin-api.service';
import { getErrorMessage } from '../../../core/utils/http-error.util';

@Component({
  selector: 'app-admin-operaciones-page',
  standalone: true,
  imports: [CommonModule],
  template: `
    <section class="space-y-5">
      <header>
        <h1 class="text-2xl font-semibold">Operaciones: talleres y mecánicos</h1>
        <p class="text-sm text-slate-500">Monitorea usuarios taller y controla disponibilidad de mecánicos.</p>
      </header>

      @if (errorMessage()) {
        <p class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ errorMessage() }}</p>
      }
      @if (successMessage()) {
        <p class="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">{{ successMessage() }}</p>
      }

      <article class="space-y-2 rounded-xl border border-slate-200 p-4">
        <h2 class="font-medium">Usuarios con rol taller</h2>
        @for (taller of talleresUsuarios(); track taller.id) {
          <p class="text-sm text-slate-600">{{ taller.nombre }} {{ taller.apellido }} · {{ taller.email }}</p>
        }
        @if (!talleresUsuarios().length) {
          <p class="text-sm text-slate-500">No hay usuarios taller disponibles.</p>
        }
      </article>

      <article class="space-y-2 rounded-xl border border-slate-200 p-4">
        <h2 class="font-medium">Mecánicos</h2>
        <div class="flex flex-wrap gap-2">
          <button class="rounded-lg border px-3 py-1 text-sm" [class.bg-slate-900]="filtroDisponibles() === null" [class.text-white]="filtroDisponibles() === null" type="button" (click)="setFiltroDisponibles(null)">Todos</button>
          <button class="rounded-lg border px-3 py-1 text-sm" [class.bg-slate-900]="filtroDisponibles() === true" [class.text-white]="filtroDisponibles() === true" type="button" (click)="setFiltroDisponibles(true)">Disponibles</button>
          <button class="rounded-lg border px-3 py-1 text-sm" [class.bg-slate-900]="filtroDisponibles() === false" [class.text-white]="filtroDisponibles() === false" type="button" (click)="setFiltroDisponibles(false)">No disponibles</button>
        </div>

        @for (mecanico of mecanicos(); track mecanico.id) {
          <div class="grid gap-2 rounded-lg border border-slate-200 p-3 sm:grid-cols-[1fr_auto] sm:items-center">
            <p class="text-sm text-slate-600">ID: {{ mecanico.id }} · Taller: {{ mecanico.taller_id }} · Especialidad: {{ mecanico.especialidad || 'general' }}</p>
            <button class="rounded-lg border px-3 py-1 text-sm" type="button" (click)="toggleDisponibilidad(mecanico)">
              {{ mecanico.disponible ? 'Marcar no disponible' : 'Marcar disponible' }}
            </button>
          </div>
        }

        @if (!mecanicos().length) {
          <p class="text-sm text-slate-500">No hay mecánicos para el filtro seleccionado.</p>
        }
      </article>
    </section>
  `,
})
export class AdminOperacionesPageComponent {
  private readonly api = inject(AdminApiService);

  protected readonly talleresUsuarios = signal<AdminUsuario[]>([]);
  protected readonly mecanicos = signal<AdminMecanico[]>([]);
  protected readonly filtroDisponibles = signal<boolean | null>(null);
  protected readonly errorMessage = signal('');
  protected readonly successMessage = signal('');

  constructor() {
    void this.load();
  }

  protected async setFiltroDisponibles(disponible: boolean | null): Promise<void> {
    this.filtroDisponibles.set(disponible);
    await this.loadMecanicos();
  }

  protected async toggleDisponibilidad(mecanico: AdminMecanico): Promise<void> {
    this.errorMessage.set('');
    this.successMessage.set('');
    try {
      await firstValueFrom(this.api.updateMecanicoDisponibilidad(mecanico.id, !mecanico.disponible));
      await this.loadMecanicos();
      this.successMessage.set('Disponibilidad de mecánico actualizada.');
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo actualizar la disponibilidad del mecánico.'));
    }
  }

  private async load(): Promise<void> {
    this.errorMessage.set('');
    try {
      const usersResponse = await firstValueFrom(this.api.listUsuarios());
      const users = usersResponse.data ?? [];
      this.talleresUsuarios.set(users.filter((u) => u.rol === 'taller'));
      await this.loadMecanicos();
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo cargar el módulo de operaciones.'));
    }
  }

  private async loadMecanicos(): Promise<void> {
    try {
      const response = await firstValueFrom(this.api.listMecanicos(this.filtroDisponibles() ?? undefined));
      this.mecanicos.set(response.data ?? []);
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudieron cargar los mecánicos.'));
    }
  }
}
