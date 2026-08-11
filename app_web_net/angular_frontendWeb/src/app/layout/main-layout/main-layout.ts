import { SesionService } from './../../services/sesion';
import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NavigationEnd, Router, RouterLink, RouterOutlet } from '@angular/router';
import { filter } from 'rxjs/operators';
import { LayoutService } from '../../interfaces/layout';
import { Topbar } from '../topbar/topbar';

// Definimos la interfaz con los nuevos tipos de iconos válidos tecnicamente
// son los iconos que se ven
interface NavItem {
  label: string;
  titulo: string;
  route: string;
  icon: 'inicio' | 'dispositivos' | 'organizaciones' | 'mapa' | 'materia-prima' | 'proveedores' | 'productos' | 'graficas' | 'compras';
  children?: string[];
}

@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterOutlet, Topbar],
  templateUrl: './main-layout.html',
  styleUrl: './main-layout.scss',
})
export class MainLayout {
  private router = inject(Router);
  layout = inject(LayoutService);
  sesionService = inject(SesionService);

 navItems: NavItem[] = [
  { label: 'Inicio', titulo: 'INICIO', route: '/inicio', icon: 'inicio' },
  { label: 'Dispositivos', titulo: 'DISPOSITIVOS', route: '/dispositivos', icon: 'dispositivos' },
  { label: 'Organizaciones', titulo: 'ORGANIZACIONES', route: '/organizaciones', icon: 'organizaciones' },
  { label: 'Materia Prima', titulo: 'MATERIA PRIMA', route: '/materiaprima', icon: 'materia-prima' },
  { label: 'Proveedores', titulo: 'PROVEEDORES', route: '/proveedores', icon: 'proveedores' },
  { label: 'Productos', titulo: 'PRODUCTOS', route: '/productos', icon: 'productos' },
  { label: 'Análisis', titulo: 'ANÁLISIS', route: '/graficas', icon: 'graficas' },
];

 navItemsClientes: NavItem[] = [
  { label: 'Inicio', titulo: 'INICIO', route: '/inicio', icon: 'inicio' },
  { label: 'Mis Compras', titulo: 'MIS COMPRAS', route: '/mis-compras', icon: 'compras' }
];

  private extraTitles: Record<string, string> = {
    '/ajustes': 'AJUSTES',
    '/mis-productos': 'MIS PRODUCTOS',
  };

  constructor() {
    const rol = this.sesionService.obtenerRol();

    if (rol === 'admin') {
      this.navItems = this.navItems;
    }

    if (rol === 'usuario') {
      this.navItems = this.navItemsClientes;
    }

    this.router.events
      .pipe(filter((e): e is NavigationEnd => e instanceof NavigationEnd))
      .subscribe(e => this.actualizarTitulo(e.urlAfterRedirects));

    this.actualizarTitulo(this.router.url);
  }

  isActive(item: NavItem): boolean {
    const url = this.router.url;
    const matchesRoute = item.route === '/' ? url === '/' : url.startsWith(item.route);
    const matchesChild = item.children?.some(c => url.startsWith(c)) ?? false;
    return matchesRoute || matchesChild;
  }

  toggleSidebar(): void {
    this.layout.toggleSidebar();
  }

  private actualizarTitulo(url: string): void {
    const navItem = this.navItems.find(i =>
      i.route === '/'
        ? url === '/'
        : url.startsWith(i.route) || (i.children?.some(c => url.startsWith(c)) ?? false)
    );
    if (navItem) {
      this.layout.setTitle(navItem.titulo);
      return;
    }
    const extraKey = Object.keys(this.extraTitles).find(route => url.startsWith(route));
    this.layout.setTitle(extraKey ? this.extraTitles[extraKey] : '');
  }

  logout(): void {
    this.sesionService.cerrarSesion();
    this.router.navigate(['/login']);
  }
}
