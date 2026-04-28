import { CommonModule } from '@angular/common';
import { Component, computed, inject } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { NgIcon, provideIcons } from '@ng-icons/core';
import {
  lucideBarChart3,
  lucideBell,
  lucideBuilding2,
  lucideCarFront,
  lucideClipboardList,
  lucideGauge,
  lucideLayoutDashboard,
  lucidePackage,
  lucideShield,
  lucideTriangleAlert,
  lucideUser,
  lucideUsers,
  lucideWrench,
} from '@ng-icons/lucide';

import {
  HlmSidebar,
  HlmSidebarContent,
  HlmSidebarHeader,
  HlmSidebarInset,
  HlmSidebarMenu,
  HlmSidebarMenuButton,
  HlmSidebarMenuItem,
  HlmSidebarTrigger,
  HlmSidebarWrapper,
} from '../../components/sidebar/src';
import { SessionService } from '../services/session.service';

type SidebarItem = {
  label: string;
  route: string;
  icon: string;
  exact?: boolean;
};

type SidebarSection = {
  title?: string;
  items: SidebarItem[];
};

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    RouterLinkActive,
    RouterOutlet,
    NgIcon,
    HlmSidebar,
    HlmSidebarContent,
    HlmSidebarHeader,
    HlmSidebarInset,
    HlmSidebarMenu,
    HlmSidebarMenuButton,
    HlmSidebarMenuItem,
    HlmSidebarTrigger,
    HlmSidebarWrapper,
  ],
  providers: [
    provideIcons({
      lucideBarChart3,
      lucideBell,
      lucideBuilding2,
      lucideCarFront,
      lucideClipboardList,
      lucideGauge,
      lucideLayoutDashboard,
      lucidePackage,
      lucideShield,
      lucideTriangleAlert,
      lucideUser,
      lucideUsers,
      lucideWrench,
    }),
  ],
  templateUrl: './app-shell.component.html',
})
export class AppShellComponent {
  private readonly session = inject(SessionService);

  protected readonly fullName = computed(() => {
    const user = this.session.user();
    return user ? `${user.nombre} ${user.apellido}` : 'Sin sesión';
  });

  protected readonly userRole = computed(() => this.session.user()?.rol ?? '-');

  protected readonly userRoleLabel = computed(() => {
    switch (this.userRole()) {
      case 'conductor':
        return 'Conductor';
      case 'taller':
        return 'Taller';
      case 'mecanico':
        return 'Mecánico';
      case 'admin':
        return 'Admin';
      default:
        return 'Sin sesión';
    }
  });

  protected readonly sidebarSections = computed<SidebarSection[]>(() => {
    const shared: SidebarSection = {
      items: [{ label: 'Mi perfil', route: '/app/perfil', icon: 'lucideUser', exact: true }],
    };

    switch (this.userRole()) {
      case 'conductor':
        return [
          shared,
          {
            title: 'Conductor',
            items: [
              { label: 'Dashboard', route: '/app/conductor', icon: 'lucideLayoutDashboard', exact: true },
              { label: 'Vehículos', route: '/app/conductor/vehiculos', icon: 'lucideCarFront' },
              { label: 'Averías', route: '/app/conductor/averias', icon: 'lucideTriangleAlert' },
              { label: 'Órdenes', route: '/app/conductor/ordenes', icon: 'lucideClipboardList' },
              { label: 'Notificaciones', route: '/app/conductor/notificaciones', icon: 'lucideBell' },
            ],
          },
        ];
      case 'taller':
        return [
          shared,
          {
            title: 'Taller',
            items: [
              { label: 'Dashboard', route: '/app/taller', icon: 'lucideLayoutDashboard', exact: true },
              { label: 'Órdenes taller', route: '/app/taller/ordenes', icon: 'lucideClipboardList' },
              { label: 'Comisiones', route: '/app/taller/comisiones', icon: 'lucideBarChart3' },
              { label: 'Servicios', route: '/app/taller/servicios', icon: 'lucideWrench' },
              { label: 'Disponibilidad', route: '/app/taller/disponibilidad', icon: 'lucideGauge' },
              { label: 'Perfil taller', route: '/app/taller/perfil', icon: 'lucideBuilding2' },
              { label: 'Notificaciones', route: '/app/taller/notificaciones', icon: 'lucideBell' },
            ],
          },
        ];
      case 'mecanico':
        return [
          shared,
          {
            title: 'Mecánico',
            items: [
              { label: 'Dashboard', route: '/app/mecanico', icon: 'lucideLayoutDashboard', exact: true },
              { label: 'Mis asignaciones', route: '/app/mecanico/asignaciones', icon: 'lucideClipboardList' },
            ],
          },
        ];
      case 'admin':
        return [
          shared,
          {
            title: 'Administración',
            items: [
              { label: 'Dashboard', route: '/app/admin', icon: 'lucideLayoutDashboard', exact: true },
              { label: 'Usuarios', route: '/app/admin/usuarios', icon: 'lucideUsers' },
              { label: 'Talleres y mecánicos', route: '/app/admin/operaciones', icon: 'lucideShield' },
              { label: 'Catálogo', route: '/app/admin/catalogo', icon: 'lucideWrench' },
              { label: 'Órdenes', route: '/app/admin/ordenes', icon: 'lucideClipboardList' },
              { label: 'Finanzas', route: '/app/admin/finanzas', icon: 'lucidePackage' },
              { label: 'Métricas', route: '/app/admin/metricas', icon: 'lucideBarChart3' },
            ],
          },
        ];
      default:
        return [shared];
    }
  });

  protected async logout(): Promise<void> {
    await this.session.logout(true);
  }
}
