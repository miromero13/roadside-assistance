import { CommonModule } from '@angular/common';
import { Component, DestroyRef, inject, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { lucideMoreVertical } from '@ng-icons/lucide';

import { AdminMecanico, AdminTaller } from '../../../core/models/admin.model';
import { AdminApiService } from '../../../core/services/admin-api.service';
import { getErrorMessage } from '../../../core/utils/http-error.util';
import { HlmButton } from '@spartan-ng/helm/button';
import { HlmIcon } from '@spartan-ng/helm/icon';
import { HlmTable } from '@spartan-ng/helm/table';

@Component({
  selector: 'app-admin-operaciones-page',
  standalone: true,
  imports: [CommonModule, HlmButton, HlmIcon, HlmTable, NgIcon, RouterLink],
  providers: [provideIcons({ lucideMoreVertical })],
  templateUrl: './admin-operaciones-page.component.html',
})
export class AdminOperacionesPageComponent {
  private readonly api = inject(AdminApiService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  private readonly destroyRef = inject(DestroyRef);

  protected readonly talleres = signal<AdminTaller[]>([]);
  protected readonly mecanicos = signal<AdminMecanico[]>([]);
  protected readonly filtroDisponibles = signal<boolean | null>(null);
  protected readonly errorMessage = signal('');
  protected readonly successMessage = signal('');
  protected readonly actionMenuOpenId = signal<string | null>(null);

  constructor() {
    this.filtroDisponibles.set(this.parseFiltro(this.route.snapshot.queryParamMap.get('disponible')));
    this.route.queryParamMap.pipe(takeUntilDestroyed(this.destroyRef)).subscribe((params) => {
      const disponible = this.parseFiltro(params.get('disponible'));
      if (disponible !== this.filtroDisponibles()) {
        this.filtroDisponibles.set(disponible);
        void this.loadMecanicos();
      }
    });
    void this.load();
  }

  protected async setFiltroDisponibles(disponible: boolean | null): Promise<void> {
    await this.router.navigate([], {
      relativeTo: this.route,
      queryParams: { disponible: disponible === null ? null : String(disponible) },
    });
  }

  protected toggleActionMenu(tallerId: string): void {
    this.actionMenuOpenId.set(this.actionMenuOpenId() === tallerId ? null : tallerId);
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
      const talleresResponse = await firstValueFrom(this.api.listTalleres());
      this.talleres.set(talleresResponse.data ?? []);
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
