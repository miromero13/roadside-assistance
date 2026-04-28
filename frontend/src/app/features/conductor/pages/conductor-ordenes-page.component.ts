import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { lucideMoreVertical, lucidePlus, lucideX } from '@ng-icons/lucide';

import {
  Averia,
  CategoriaServicio,
  Orden,
  TallerCandidato,
} from '../../../core/models/conductor.model';
import { ConductorApiService } from '../../../core/services/conductor-api.service';
import { getErrorMessage } from '../../../core/utils/http-error.util';
import { HlmButton } from '../../../components/button/src';
import { HlmSelectImports } from '../../../components/select/src';
import { HlmTable } from '../../../components/table/src';
import { HlmTextarea } from '../../../components/textarea/src';

@Component({
  selector: 'app-conductor-ordenes-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink, HlmButton, HlmTable, HlmTextarea, NgIcon, ...HlmSelectImports],
  providers: [provideIcons({ lucideMoreVertical, lucidePlus, lucideX })],
  templateUrl: './conductor-ordenes-page.component.html',
})
export class ConductorOrdenesPageComponent {
  private readonly fb = inject(FormBuilder);
  private readonly api = inject(ConductorApiService);

  protected readonly averias = signal<Averia[]>([]);
  protected readonly categorias = signal<CategoriaServicio[]>([]);
  protected readonly candidatos = signal<TallerCandidato[]>([]);
  protected readonly ordenes = signal<Orden[]>([]);
  protected readonly errorMessage = signal('');
  protected readonly createModalOpen = signal(false);
  protected readonly actionMenuOpenId = signal<string | null>(null);

  protected readonly crearOrdenForm = this.fb.nonNullable.group({
    averia_id: ['', Validators.required],
    categoria_id: ['', Validators.required],
    es_domicilio: true,
    notas_conductor: '',
  });

  constructor() {
    void this.loadData();
  }

  protected openCreateModal(): void {
    this.actionMenuOpenId.set(null);
    this.candidatos.set([]);
    this.crearOrdenForm.reset({
      averia_id: '',
      categoria_id: '',
      es_domicilio: true,
      notas_conductor: '',
    });
    this.createModalOpen.set(true);
  }

  protected closeCreateModal(): void {
    this.createModalOpen.set(false);
  }

  protected toggleActionMenu(ordenId: string): void {
    this.actionMenuOpenId.set(this.actionMenuOpenId() === ordenId ? null : ordenId);
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
      this.closeCreateModal();
      await this.loadOrdenes();
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo crear la orden.'));
    }
  }

  protected async cancelarOrden(ordenId: string): Promise<void> {
    this.errorMessage.set('');
    try {
      await firstValueFrom(this.api.cancelOrden(ordenId, 'Cancelada desde frontend conductor'));
      this.actionMenuOpenId.set(null);
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
