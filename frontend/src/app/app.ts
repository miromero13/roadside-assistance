import { Component } from '@angular/core';

import { HlmAvatarImports } from '@spartan-ng/helm/avatar';
import { HlmBadgeImports } from '@spartan-ng/helm/badge';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmCardImports } from '@spartan-ng/helm/card';
import { HlmSeparatorImports } from '@spartan-ng/helm/separator';
import { HlmSidebarImports } from '@spartan-ng/helm/sidebar';

@Component({
  selector: 'app-root',
  imports: [
    ...HlmAvatarImports,
    ...HlmBadgeImports,
    ...HlmButtonImports,
    ...HlmCardImports,
    ...HlmSeparatorImports,
    ...HlmSidebarImports,
  ],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = 'Roadside Assistance';

  protected readonly sidebarItems = [
    { label: 'Dashboard', href: '#', active: true },
    { label: 'Servicios', href: '#', active: false },
    { label: 'Vehículos', href: '#', active: false },
    { label: 'Solicitudes', href: '#', active: false },
    { label: 'Configuración', href: '#', active: false },
  ];
}
