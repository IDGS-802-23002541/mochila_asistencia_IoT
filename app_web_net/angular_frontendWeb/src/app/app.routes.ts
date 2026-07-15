import { Routes } from '@angular/router';
import { Home } from './pages/home/home';
import { Graficas } from './pages/graficas/graficas';

export const routes: Routes = [
  {
    path: '',
    component: Home
  },
  {
    path: 'graficas/dashboard',
    component: Graficas
  }
];
