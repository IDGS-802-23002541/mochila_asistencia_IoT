import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

interface NavItem {
  label: string;
  route: string;
  icon: 'inicio' | 'dispositivos' | 'mapa' | 'graficas';
}

@Component({
  selector: 'app-main-layout',
  imports: [CommonModule, RouterLink, RouterLinkActive, RouterOutlet],
  standalone: true,
  templateUrl: './main-layout.html',
  styleUrl: './main-layout.scss',
})
export class MainLayout {
  private router = inject(Router);
  navItems: NavItem[] = [
    { label: 'Inicio', route: '/', icon: 'inicio' },
    { label: 'Dispositivos', route: '/dispositivos', icon: 'dispositivos' },
    { label: 'Mapa', route: '/mapa', icon: 'mapa' },
    { label: 'Gráficas', route: '/graficas', icon: 'graficas' }
  ];

  logout(): void {
    // TODO: limpiar token / sesión real aquí
    this.router.navigate(['/login']);
  }
}