import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { firstValueFrom } from 'rxjs';

import { AdminCategoriaServicio, AdminServicioTaller } from '../../../core/models/admin.model';
import { AdminApiService } from '../../../core/services/admin-api.service';
import { getErrorMessage } from '../../../core/utils/http-error.util';

@Component({
  selector: 'app-admin-catalogo-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <section class="space-y-5">
      <header>
        <h1 class="text-2xl font-semibold">Catálogo y servicios</h1>
        <p class="text-sm text-slate-500">Administra categorías y consulta servicios por taller.</p>
      </header>

      @if (errorMessage()) {
        <p class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ errorMessage() }}</p>
      }
      @if (successMessage()) {
        <p class="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">{{ successMessage() }}</p>
      }

      <form class="grid gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4 sm:grid-cols-2" [formGroup]="crearCategoriaForm" (ngSubmit)="crearCategoria()">
        <input class="rounded-lg border border-slate-300 px-3 py-2" placeholder="Nombre categoría" formControlName="nombre" />
        <input class="rounded-lg border border-slate-300 px-3 py-2" placeholder="Descripción" formControlName="descripcion" />
        <button class="w-fit rounded-lg bg-slate-900 px-4 py-2 text-sm text-white sm:col-span-2" type="submit">Crear categoría</button>
      </form>

      <article class="space-y-2 rounded-xl border border-slate-200 p-4">
        <h2 class="font-medium">Categorías de servicio</h2>
        @for (categoria of categorias(); track categoria.id) {
          <div class="grid gap-2 rounded-lg border border-slate-200 p-3 sm:grid-cols-[1fr_auto] sm:items-center">
            <p class="text-sm text-slate-600">{{ categoria.nombre }} · {{ categoria.descripcion || 'Sin descripción' }} · {{ categoria.activo ? 'activa' : 'inactiva' }}</p>
            <button class="rounded-lg border px-3 py-1 text-sm" type="button" (click)="toggleCategoria(categoria)">
              {{ categoria.activo ? 'Desactivar' : 'Activar' }}
            </button>
          </div>
        }
      </article>

      <form class="grid gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4 sm:grid-cols-[1fr_auto]" [formGroup]="buscarServiciosForm" (ngSubmit)="buscarServicios()">
        <input class="rounded-lg border border-slate-300 px-3 py-2" placeholder="Taller ID" formControlName="tallerId" />
        <button class="w-fit rounded-lg border border-slate-300 px-4 py-2 text-sm" type="submit">Consultar servicios</button>
      </form>

      <article class="space-y-2 rounded-xl border border-slate-200 p-4">
        <h2 class="font-medium">Servicios del taller consultado</h2>
        @for (servicio of serviciosTaller(); track servicio.id) {
          <p class="text-sm text-slate-600">{{ servicio.id }} · categoría {{ servicio.categoria_id }} · {{ servicio.activo ? 'activo' : 'inactivo' }}</p>
        }
        @if (!serviciosTaller().length) {
          <p class="text-sm text-slate-500">Sin servicios cargados para la consulta actual.</p>
        }
      </article>
    </section>
  `,
})
export class AdminCatalogoPageComponent {
  private readonly api = inject(AdminApiService);
  private readonly fb = inject(FormBuilder);

  protected readonly categorias = signal<AdminCategoriaServicio[]>([]);
  protected readonly serviciosTaller = signal<AdminServicioTaller[]>([]);
  protected readonly errorMessage = signal('');
  protected readonly successMessage = signal('');

  protected readonly crearCategoriaForm = this.fb.nonNullable.group({
    nombre: ['', Validators.required],
    descripcion: '',
  });

  protected readonly buscarServiciosForm = this.fb.nonNullable.group({
    tallerId: ['', Validators.required],
  });

  constructor() {
    void this.loadCategorias();
  }

  protected async crearCategoria(): Promise<void> {
    if (this.crearCategoriaForm.invalid) {
      this.crearCategoriaForm.markAllAsTouched();
      return;
    }
    this.errorMessage.set('');
    this.successMessage.set('');
    try {
      const payload = this.crearCategoriaForm.getRawValue();
      await firstValueFrom(this.api.createCategoria(payload.nombre, payload.descripcion || null));
      this.crearCategoriaForm.reset({ nombre: '', descripcion: '' });
      await this.loadCategorias();
      this.successMessage.set('Categoría creada correctamente.');
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo crear la categoría.'));
    }
  }

  protected async toggleCategoria(categoria: AdminCategoriaServicio): Promise<void> {
    this.errorMessage.set('');
    this.successMessage.set('');
    try {
      await firstValueFrom(this.api.updateCategoria(categoria.id, { activo: !categoria.activo }));
      await this.loadCategorias();
      this.successMessage.set('Categoría actualizada correctamente.');
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo actualizar la categoría.'));
    }
  }

  protected async buscarServicios(): Promise<void> {
    if (this.buscarServiciosForm.invalid) {
      this.buscarServiciosForm.markAllAsTouched();
      return;
    }
    this.errorMessage.set('');
    try {
      const { tallerId } = this.buscarServiciosForm.getRawValue();
      const response = await firstValueFrom(this.api.listServiciosTaller(tallerId));
      this.serviciosTaller.set(response.data ?? []);
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudieron consultar servicios del taller.'));
    }
  }

  private async loadCategorias(): Promise<void> {
    const response = await firstValueFrom(this.api.listCategorias(undefined));
    this.categorias.set(response.data ?? []);
  }
}
