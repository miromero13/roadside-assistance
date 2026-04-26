import { CommonModule } from '@angular/common';
import { Component, effect, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { firstValueFrom } from 'rxjs';

import { SessionService } from '../../../core/services/session.service';
import { UserApiService } from '../../../core/services/user-api.service';

@Component({
  selector: 'app-profile-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <section>
      <h1 class="text-2xl font-semibold">Mi perfil</h1>
      <p class="mt-1 text-sm text-slate-500">Actualiza tus datos personales y contraseña.</p>

      <form class="mt-6 grid gap-4" [formGroup]="form" (ngSubmit)="submit()">
        <div class="grid gap-4 sm:grid-cols-2">
          <label class="block space-y-1">
            <span class="text-sm font-medium">Nombre</span>
            <input class="w-full rounded-lg border border-slate-300 px-3 py-2" formControlName="nombre" />
          </label>
          <label class="block space-y-1">
            <span class="text-sm font-medium">Apellido</span>
            <input class="w-full rounded-lg border border-slate-300 px-3 py-2" formControlName="apellido" />
          </label>
        </div>

        <div class="grid gap-4 sm:grid-cols-2">
          <label class="block space-y-1">
            <span class="text-sm font-medium">Teléfono</span>
            <input class="w-full rounded-lg border border-slate-300 px-3 py-2" formControlName="telefono" />
          </label>
          <label class="block space-y-1">
            <span class="text-sm font-medium">Foto URL</span>
            <input class="w-full rounded-lg border border-slate-300 px-3 py-2" formControlName="foto_url" />
          </label>
        </div>

        <div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <p class="text-sm font-medium">Cambio de contraseña (opcional)</p>
          <div class="mt-3 grid gap-4 sm:grid-cols-2">
            <label class="block space-y-1">
              <span class="text-sm">Contraseña actual</span>
              <input
                class="w-full rounded-lg border border-slate-300 px-3 py-2"
                type="password"
                formControlName="password_actual"
              />
            </label>
            <label class="block space-y-1">
              <span class="text-sm">Nueva contraseña</span>
              <input
                class="w-full rounded-lg border border-slate-300 px-3 py-2"
                type="password"
                formControlName="password_nueva"
              />
            </label>
          </div>
        </div>

        @if (errorMessage()) {
          <p class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ errorMessage() }}</p>
        }
        @if (successMessage()) {
          <p class="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
            {{ successMessage() }}
          </p>
        }

        <div>
          <button
            class="rounded-lg bg-slate-900 px-4 py-2 text-white disabled:cursor-not-allowed disabled:opacity-60"
            type="submit"
            [disabled]="loading()"
          >
            {{ loading() ? 'Guardando...' : 'Guardar cambios' }}
          </button>
        </div>
      </form>
    </section>
  `,
})
export class ProfilePageComponent {
  private readonly fb = inject(FormBuilder);
  private readonly session = inject(SessionService);
  private readonly usersApi = inject(UserApiService);

  protected readonly loading = signal(false);
  protected readonly errorMessage = signal('');
  protected readonly successMessage = signal('');

  protected readonly form = this.fb.nonNullable.group({
    nombre: '',
    apellido: '',
    telefono: '',
    foto_url: '',
    password_actual: '',
    password_nueva: '',
  });

  constructor() {
    effect(() => {
      const user = this.session.user();
      if (!user) {
        return;
      }

      this.form.patchValue({
        nombre: user.nombre,
        apellido: user.apellido,
        telefono: user.telefono,
        foto_url: user.foto_url ?? '',
      });
    });
  }

  protected async submit(): Promise<void> {
    this.loading.set(true);
    this.errorMessage.set('');
    this.successMessage.set('');

    const raw = this.form.getRawValue();
    const payload: Record<string, string> = {
      nombre: raw.nombre,
      apellido: raw.apellido,
      telefono: raw.telefono,
      foto_url: raw.foto_url,
    };

    if (raw.password_actual || raw.password_nueva) {
      payload['password_actual'] = raw.password_actual;
      payload['password_nueva'] = raw.password_nueva;
    }

    try {
      await firstValueFrom(this.usersApi.updateMe(payload));
      await this.session.refreshMe();
      this.form.patchValue({ password_actual: '', password_nueva: '' });
      this.successMessage.set('Perfil actualizado correctamente.');
    } catch {
      this.errorMessage.set('No se pudo actualizar el perfil. Revisa los datos.');
    } finally {
      this.loading.set(false);
    }
  }
}
