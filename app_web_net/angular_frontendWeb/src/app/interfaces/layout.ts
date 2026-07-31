import { Injectable, signal } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class LayoutService {
  // true = sidebar colapsado (solo íconos en desktop / oculto en móvil)
  sidebarCollapsed = signal(
    typeof window !== 'undefined' ? window.innerWidth <= 780 : false
  );

  currentTitle = signal('INICIO');

  toggleSidebar(): void {
    this.sidebarCollapsed.update(v => !v);
  }

  setTitle(title: string): void {
    this.currentTitle.set(title);
  }
}
