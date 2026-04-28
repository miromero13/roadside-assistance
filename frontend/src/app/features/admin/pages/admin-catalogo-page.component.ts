import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { firstValueFrom } from 'rxjs';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { lucideMoreVertical, lucidePlus, lucideX } from '@ng-icons/lucide';

import { AdminCategoriaServicio } from '../../../core/models/admin.model';
import { AdminApiService } from '../../../core/services/admin-api.service';
import { getErrorMessage } from '../../../core/utils/http-error.util';
import { HlmButton } from '@spartan-ng/helm/button';
import { HlmIcon } from '@spartan-ng/helm/icon';
import { HlmTable } from '@spartan-ng/helm/table';
import { HlmTextarea } from '@spartan-ng/helm/textarea';

@Component({
  selector: 'app-admin-catalogo-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, HlmButton, HlmIcon, HlmTable, HlmTextarea, NgIcon],
  providers: [provideIcons({ lucideMoreVertical, lucidePlus, lucideX })],
  templateUrl: './admin-catalogo-page.component.html',
})
export class AdminCatalogoPageComponent {
  private readonly api = inject(AdminApiService);
  private readonly fb = inject(FormBuilder);

  protected readonly categorias = signal<AdminCategoriaServicio[]>([]);
  protected readonly errorMessage = signal('');
  protected readonly successMessage = signal('');
  protected readonly categoriaModalOpen = signal(false);
  protected readonly categoriaMenuOpenId = signal<string | null>(null);

  protected readonly crearCategoriaForm = this.fb.nonNullable.group({
    nombre: ['', Validators.required],
    descripcion: '',
  });

  constructor() {
    void this.loadCategorias();
  }

  protected openCategoriaModal(): void {
    this.categoriaMenuOpenId.set(null);
    this.crearCategoriaForm.reset({ nombre: '', descripcion: '' });
    this.categoriaModalOpen.set(true);
  }

  protected closeCategoriaModal(): void {
    this.categoriaModalOpen.set(false);
  }

  protected toggleCategoriaMenu(categoriaId: string): void {
    this.categoriaMenuOpenId.set(this.categoriaMenuOpenId() === categoriaId ? null : categoriaId);
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
      this.closeCategoriaModal();
      await this.loadCategorias();
      this.successMessage.set('Categoría creada correctamente.');
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo crear la categoría.'));
    }
  }

  protected async toggleCategoria(categoria: AdminCategoriaServicio): Promise<void> {
    this.categoriaMenuOpenId.set(null);
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

  private async loadCategorias(): Promise<void> {
    const response = await firstValueFrom(this.api.listCategorias(undefined));
    this.categorias.set(response.data ?? []);
  }
}
