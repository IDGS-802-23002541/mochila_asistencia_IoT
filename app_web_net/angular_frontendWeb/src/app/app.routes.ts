import { Routes } from '@angular/router';

import { Home } from './pages/home/home';
import { Login } from './pages/login/login';
import { Inicio } from './pages/inicio/inicio';
import { MainLayout } from './layout/main-layout/main-layout';
import { Graficas } from './pages/graficas/graficas';

export const routes: Routes = [
  {
    path: '',
    component: Home
  },
  {
    path: 'login',
    component: Login
  },
  {
    path: '',
    component: MainLayout,
    children: [
      {
        path: 'inicio',
        component: Inicio
      },
      {
        path: 'graficas/dashboard',
        component: Graficas
      }

      // {
      //   path: 'dispositivos',
      //   component: Dispositivos
      // },

      // {
      //   path: 'mapa',
      //   component: Mapa
      // },

      // {
      //   path: 'graficas',
      //   component: Graficas
      // }
    ]
  }
];
