import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

// Definimos la interfaz con los nuevos tipos de iconos válidos tecnicamente
// son los iconos que se ven
interface NavItem {
  label: string;
  route: string;
  icon: 'inicio' | 'dispositivos' | 'mapa' | 'graficas' | 'instituciones' | 'proveedores' | 'materia-prima';
}

@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive, RouterOutlet],
  templateUrl: './main-layout.html',
  styleUrl: './main-layout.scss',
})
export class MainLayout {
  private router = inject(Router);

  // Arreglo de navegación con las nuevas rutas incluidas quedan pendientes las de mena
 navItems: NavItem[] = [
  { label: 'Inicio', route: '/inicio', icon: 'inicio' },
  { label: 'Dispositivos', route: '/dispositivos', icon: 'dispositivos' },
  { label: 'Gráficas', route: '/graficas', icon: 'graficas' },
  { label: 'Mapa de Calor', route: '/analitica/mapa-calor', icon: 'mapa' },

  // Estos se quedarán listos para cuando tengamos las páginas correspondientes
  { label: 'Instituciones', route: '/instituciones', icon: 'instituciones' },
  { label: 'Proveedores', route: '/proveedores', icon: 'proveedores' },
  { label: 'Materia Prima', route: '/materia-prima', icon: 'materia-prima' }
];
  logout(): void {
    // TODO: limpiar token / sesión real aquí si es que la hacemos
    this.router.navigate(['/login']);
  }
}
