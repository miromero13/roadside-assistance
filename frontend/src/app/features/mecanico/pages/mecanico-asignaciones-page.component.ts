import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';

import { AsignacionMecanico } from '../../../core/models/mecanico.model';
import { MecanicoApiService } from '../../../core/services/mecanico-api.service';
import { getErrorMessage } from '../../../core/utils/http-error.util';

@Component({
  selector: 'app-mecanico-asignaciones-page',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './mecanico-asignaciones-page.component.html',
})
export class MecanicoAsignacionesPageComponent {
  private readonly api = inject(MecanicoApiService);

  protected readonly asignaciones = signal<AsignacionMecanico[]>([]);
  protected readonly filtroEstado = signal('');
  protected readonly errorMessage = signal('');

  protected readonly asignacionesFiltradas = signal<AsignacionMecanico[]>([]);

  constructor() {
    void this.loadAsignaciones();
  }

  protected setFiltro(estado: string): void {
    this.filtroEstado.set(estado);
    this.applyFiltro();
  }

  private applyFiltro(): void {
    const estado = this.filtroEstado();
    const all = this.asignaciones();
    this.asignacionesFiltradas.set(estado ? all.filter((item) => item.estado === estado) : all);
  }

  private async loadAsignaciones(): Promise<void> {
    this.errorMessage.set('');
    try {
      const response = await firstValueFrom(this.api.listAsignacionesMias());
      this.asignaciones.set(response.data ?? []);
      this.applyFiltro();
    } catch (error) {
      this.errorMessage.set(getErrorMessage(error, 'No se pudieron cargar tus asignaciones.'));
    }
  }
}
