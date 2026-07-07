import { Routes } from '@angular/router';
import { Home } from './pages/home/home';
import { MapaCalor } from './pages/analitica/mapa-calor/mapa-calor';

export const routes: Routes = [
  {
    path: '',
    component: Home
  },
  {
    path: 'analitica/mapa-calor',
    component: MapaCalor
  }
];
