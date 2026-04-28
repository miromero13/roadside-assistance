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
  templateUrl: './profile-page.component.html',
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
