import { Routes } from '@angular/router';
import { MainLayout } from './layout/main-layout/main-layout';
import { Home } from './pages/home/home';
import { Login } from './pages/login/login';

// Componentes del Menú son las importaciones paa que jale las pantallas
import { Inicio } from './pages/inicio/inicio';
import { Ajustes } from './pages/ajustes/ajustes';
import { Graficas } from './pages/graficas/graficas';
import { MapaCalor } from './pages/analitica/mapa-calor/mapa-calor';
import { Dispositivos } from './pages/dispositivos/dispositivos';

export const routes: Routes = [
  {
    path: 'login',
    component: Login
  },
  {
    path: 'welcome',
    component: Home
  },
  {
    path: '',
    component: MainLayout,
    children: [
      {
        path: '',
        redirectTo: 'inicio',
        pathMatch: 'full'
      },
      {
        path: 'inicio',
        component: Inicio
      },
      {
        path: 'analitica/mapa-calor',
        component: MapaCalor
      },
      {
        path: 'graficas',
        component: Graficas
      },
      {
        path: 'ajustes',
        component: Ajustes
      },
      {
        path: 'dispositivos',
        component: Dispositivos },

      // Espacio para las demás páginas nuevas:
      // { path: 'instituciones', component: Instituciones },
      // { path: 'proveedores', component: Proveedores },
      // { path: 'materia-prima', component: MateriaPrima }
    ]
  }
];
