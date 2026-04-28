import { CommonModule } from '@angular/common';
import { Component, DestroyRef, computed, inject, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

import { AdminApiService } from '../../../core/services/admin-api.service';
import {
  AdminCategoriaServicio,
  AdminMecanico,
  AdminTaller,
  AdminServicioTaller,
} from '../../../core/models/admin.model';
import { getErrorMessage } from '../../../core/utils/http-error.util';
import { HlmTable } from '@spartan-ng/helm/table';

@Component({
  selector: 'app-admin-operaciones-detalle-page',
  standalone: true,
  imports: [CommonModule, HlmTable, RouterLink],
  templateUrl: './admin-operaciones-detalle-page.component.html',
})
export class AdminOperacionesDetallePageComponent {
  private readonly api = inject(AdminApiService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly destroyRef = inject(DestroyRef);

  private readonly tallerId = signal<string | null>(this.route.snapshot.paramMap.get('tallerId'));
  protected readonly taller = signal<AdminTaller | null>(null);
  protected readonly mecanicos = signal<AdminMecanico[]>([]);
  protected readonly servicios = signal<AdminServicioTaller[]>([]);
  protected readonly categorias = signal<AdminCategoriaServicio[]>([]);
  protected readonly filtroDisponibles = signal<boolean | null>(null);
  protected readonly errorMessage = signal('');
  protected readonly successMessage = signal('');
  protected readonly activeTab = signal<'mecanicos' | 'servicios'>('mecanicos');

  protected readonly mecanicosDelTaller = computed(() => {
    return this.mecanicos();
  });

  protected readonly serviciosConCategoria = computed(() => {
    const categoriasPorId = new Map(this.categorias().map((categoria) => [categoria.id, categoria] as const));
    return this.servicios().map((servicio) => ({
      ...servicio,
      categoria: categoriasPorId.get(servicio.categoria_id) ?? null,
    }));
  });

  constructor() {
    this.filtroDisponibles.set(this.parseFiltro(this.route.snapshot.queryParamMap.get('disponible')));
    this.route.queryParamMap.pipe(takeUntilDestroyed(this.destroyRef)).subscribe((params) => {
      const disponible = this.parseFiltro(params.get('disponible'));
      if (disponible !== this.filtroDisponibles()) {
        this.filtroDisponibles.set(disponible);
        void this.loadMecanicos();
      }
    });
    void this.loadAll();
  }

  protected setActiveTab(tab: 'mecanicos' | 'servicios'): void {
    this.activeTab.set(tab);
  }

  protected async setFiltroDisponibles(disponible: boolean | null): Promise<void> {
    await this.router.navigate([], {
      relativeTo: this.route,
      queryParams: { disponible: disponible === null ? null : String(disponible) },
    });
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

  private async loadAll(): Promise<void> {
    const tallerId = this.route.snapshot.paramMap.get('tallerId');
    if (!tallerId) {
      this.errorMessage.set('No se recibió un taller válido.');
      return;
    }

    this.errorMessage.set('');
    try {
      const [talleresResponse, mecanicosResponse, serviciosResponse, categoriasResponse] = await Promise.all([
        firstValueFrom(this.api.listTalleres()),
        firstValueFrom(this.api.listMecanicosPorTaller(tallerId, this.filtroDisponibles() ?? undefined)),
        firstValueFrom(this.api.listServiciosTaller(tallerId)),
        firstValueFrom(this.api.listCategorias(undefined)),
      ]);

      this.taller.set((talleresResponse.data ?? []).find((item) => item.id === tallerId) ?? null);
      this.mecanicos.set(mecanicosResponse.data ?? []);
      this.servicios.set(serviciosResponse.data ?? []);
      this.categorias.set(categoriasResponse.data ?? []);
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudo cargar el detalle del taller.'));
    }
  }

  private async loadMecanicos(): Promise<void> {
    const tallerId = this.tallerId();
    if (!tallerId) {
      return;
    }
    try {
      const response = await firstValueFrom(
        this.api.listMecanicosPorTaller(tallerId, this.filtroDisponibles() ?? undefined),
      );
      this.mecanicos.set(response.data ?? []);
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudieron cargar los mecánicos.'));
    }
  }

  private parseFiltro(value: string | null): boolean | null {
    if (value === 'true') {
      return true;
    }
    if (value === 'false') {
      return false;
    }
    return null;
  }
}
