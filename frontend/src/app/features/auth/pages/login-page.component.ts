import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { SessionService } from '../../../core/services/session.service';
import { getDefaultRouteForRole } from '../../../core/utils/role-route.util';

@Component({
  selector: 'app-login-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  template: `
    <div class="min-h-screen bg-slate-100 px-4 py-10">
      <div class="mx-auto max-w-md rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h1 class="text-2xl font-semibold">Iniciar sesión</h1>
        <p class="mt-1 text-sm text-slate-500">Accede al panel de asistencia</p>

        <form class="mt-6 space-y-4" [formGroup]="form" (ngSubmit)="submit()">
          <label class="block space-y-1">
            <span class="text-sm font-medium">Correo</span>
            <input class="w-full rounded-lg border border-slate-300 px-3 py-2" type="email" formControlName="email" />
          </label>

          <label class="block space-y-1">
            <span class="text-sm font-medium">Contraseña</span>
            <input
              class="w-full rounded-lg border border-slate-300 px-3 py-2"
              type="password"
              formControlName="password"
            />
          </label>

          @if (errorMessage()) {
            <p class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ errorMessage() }}</p>
          }

          <button
            class="w-full rounded-lg bg-slate-900 px-4 py-2 font-medium text-white disabled:cursor-not-allowed disabled:opacity-60"
            type="submit"
            [disabled]="form.invalid || loading()"
          >
            {{ loading() ? 'Ingresando...' : 'Ingresar' }}
          </button>
        </form>

        <p class="mt-4 text-sm text-slate-600">
          ¿No tienes cuenta?
          <a routerLink="/auth/register" class="font-medium text-slate-900 underline">Regístrate como conductor</a>
        </p>
      </div>
    </div>
  `,
})
export class LoginPageComponent {
  private readonly fb = inject(FormBuilder);
  private readonly session = inject(SessionService);
  private readonly router = inject(Router);

  protected readonly loading = signal(false);
  protected readonly errorMessage = signal('');

  protected readonly form = this.fb.nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required]],
  });

  protected async submit(): Promise<void> {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.loading.set(true);
    this.errorMessage.set('');
    try {
      const { email, password } = this.form.getRawValue();
      await this.session.login(email, password);
      await this.router.navigateByUrl(getDefaultRouteForRole(this.session.user()?.rol));
    } catch {
      this.errorMessage.set('No se pudo iniciar sesión. Verifica tus credenciales.');
    } finally {
      this.loading.set(false);
    }
  }
}
