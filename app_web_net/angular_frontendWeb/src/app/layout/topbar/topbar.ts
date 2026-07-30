import { Component, inject } from '@angular/core';
import { LayoutService } from '../../interfaces/layout';

@Component({
  selector: 'app-topbar',
  standalone: true,
  templateUrl: './topbar.html',
  styleUrl: './topbar.css',
})
export class Topbar {
  layout = inject(LayoutService);

  toggle(): void {
    this.layout.toggleSidebar();
  }
}
