import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';

import {
  Averia,
  CategoriaServicio,
  Orden,
  TallerCandidato,
} from '../../../core/models/conductor.model';
import { ConductorApiService } from '../../../core/services/conductor-api.service';
import { getErrorMessage } from '../../../core/utils/http-error.util';

@Component({
  selector: 'app-conductor-ordenes-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  template: `
    <section class="space-y-5">
      <header>
        <h1 class="text-2xl font-semibold">Órdenes de servicio</h1>
        <p class="text-sm text-slate-500">Busca talleres candidatos y crea una orden para tu avería.</p>
      </header>

      <form class="grid gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4 sm:grid-cols-2" [formGroup]="crearOrdenForm" (ngSubmit)="buscarCandidatos()">
        <select class="rounded-lg border border-slate-300 px-3 py-2" formControlName="averia_id">
          <option value="">Selecciona avería</option>
          @for (averia of averias(); track averia.id) {
            <option [value]="averia.id">{{ averia.descripcion_conductor }}</option>
          }
        </select>

        <select class="rounded-lg border border-slate-300 px-3 py-2" formControlName="categoria_id">
          <option value="">Selecciona categoría</option>
          @for (categoria of categorias(); track categoria.id) {
            <option [value]="categoria.id">{{ categoria.nombre }}</option>
          }
        </select>

        <label class="sm:col-span-2 flex items-center gap-2 text-sm">
          <input type="checkbox" formControlName="es_domicilio" />
          Solicitar atención a domicilio
        </label>

        <textarea class="sm:col-span-2 rounded-lg border border-slate-300 px-3 py-2" rows="2" placeholder="Notas para el taller" formControlName="notas_conductor"></textarea>

        <button class="w-fit rounded-lg bg-slate-900 px-4 py-2 text-sm text-white" type="submit">Buscar talleres</button>
      </form>

      @if (candidatos().length) {
        <div class="space-y-2">
          <h2 class="font-medium">Talleres candidatos</h2>
          @for (candidato of candidatos(); track candidato.id) {
            <article class="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-slate-200 p-3">
              <div>
                <p class="font-medium">{{ candidato.nombre }}</p>
                <p class="text-sm text-slate-500">{{ candidato.distancia_km | number: '1.1-1' }} km · {{ candidato.direccion }}</p>
              </div>
              <button class="rounded-lg border border-slate-300 px-3 py-1 text-sm" type="button" (click)="crearOrden(candidato.id)">
                Crear orden
              </button>
            </article>
          }
        </div>
      }

      @if (errorMessage()) {
        <p class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ errorMessage() }}</p>
      }

      <div class="space-y-2">
        <h2 class="font-medium">Mis órdenes</h2>
        @for (orden of ordenes(); track orden.id) {
          <article class="space-y-2 rounded-xl border border-slate-200 p-3">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <p class="font-medium">Orden {{ orden.id.slice(0, 8) }} · {{ orden.estado }}</p>
              <span class="text-xs text-slate-500">{{ orden.creado_en | date: 'short' }}</span>
            </div>
            <p class="text-sm text-slate-500">Taller: {{ orden.taller_id }}</p>
            <div class="flex flex-wrap gap-2">
              <a class="rounded-lg border border-slate-300 px-3 py-1 text-sm" [routerLink]="['/app/conductor/ordenes', orden.id]">Ver detalle</a>
              @if (orden.estado === 'pendiente_respuesta' || orden.estado === 'aceptada' || orden.estado === 'tecnico_asignado') {
                <button class="rounded-lg border border-red-300 px-3 py-1 text-sm text-red-700" type="button" (click)="cancelarOrden(orden.id)">
                  Cancelar
                </button>
              }
            </div>
          </article>
        }

        @if (!ordenes().length) {
          <p class="rounded-lg border border-dashed border-slate-300 px-3 py-4 text-sm text-slate-500">Aún no tienes órdenes registradas.</p>
        }
      </div>
    </section>
  `,
})
export class ConductorOrdenesPageComponent {
  private readonly fb = inject(FormBuilder);
  private readonly api = inject(ConductorApiService);

  protected readonly averias = signal<Averia[]>([]);
  protected readonly categorias = signal<CategoriaServicio[]>([]);
  protected readonly candidatos = signal<TallerCandidato[]>([]);
  protected readonly ordenes = signal<Orden[]>([]);
  protected readonly errorMessage = signal('');

  protected readonly crearOrdenForm = this.fb.nonNullable.group({
    averia_id: ['', Validators.required],
    categoria_id: ['', Validators.required],
    es_domicilio: true,
    notas_conductor: '',
  });

  constructor() {
    void this.loadData();
  }

  protected async buscarCandidatos(): Promise<void> {
    if (this.crearOrdenForm.invalid) {
      this.crearOrdenForm.markAllAsTouched();
      return;
    }
    const { averia_id, categoria_id } = this.crearOrdenForm.getRawValue();
    this.errorMessage.set('');
    try {
      const response = await firstValueFrom(this.api.listTalleresCandidatos(averia_id, categoria_id));
      this.candidatos.set(response.data ?? []);
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudieron buscar talleres candidatos.'));
    }
  }

  protected async crearOrden(tallerId: string): Promise<void> {
    const payload = this.crearOrdenForm.getRawValue();
    this.errorMessage.set('');
    try {
      await firstValueFrom(
        this.api.createOrden({
          averia_id: payload.averia_id,
          categoria_id: payload.categoria_id,
          taller_id: tallerId,
          es_domicilio: payload.es_domicilio,
          notas_conductor: payload.notas_conductor,
        }),
      );
      this.candidatos.set([]);
      await this.loadOrdenes();
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo crear la orden.'));
    }
  }

  protected async cancelarOrden(ordenId: string): Promise<void> {
    this.errorMessage.set('');
    try {
      await firstValueFrom(this.api.cancelOrden(ordenId, 'Cancelada desde frontend conductor'));
      await this.loadOrdenes();
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo cancelar la orden.'));
    }
  }

  private async loadData(): Promise<void> {
    await Promise.all([this.loadAverias(), this.loadCategorias(), this.loadOrdenes()]);
  }

  private async loadAverias(): Promise<void> {
    const response = await firstValueFrom(this.api.listAverias());
    this.averias.set(response.data ?? []);
  }

  private async loadCategorias(): Promise<void> {
    const response = await firstValueFrom(this.api.listCategorias());
    this.categorias.set(response.data ?? []);
  }

  private async loadOrdenes(): Promise<void> {
    const response = await firstValueFrom(this.api.listOrdenes());
    this.ordenes.set(response.data ?? []);
  }
}
