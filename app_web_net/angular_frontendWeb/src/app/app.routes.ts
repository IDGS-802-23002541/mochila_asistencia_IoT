import { Routes } from '@angular/router';
import { Home } from './pages/home/home';
import { MapaCalor } from './pages/analitica/mapa-calor/mapa-calor';
import { Organizacion } from './interfaces/organizacion';
import { OrganizacionDetalle } from './pages/organizaciones/organizacion-detalle/organizacion-detalle';
import { OrganizacionesList } from './pages/organizaciones/organizaciones-list/organizaciones-list';
import { OrganizacionEditar } from './pages/organizaciones/organizacion-editar/organizacion-editar';
import { OrganizacionNuevo } from './pages/organizaciones/organizacion-nuevo/organizacion-nuevo';
import { Login } from './pages/login/login';
import { Inicio } from './pages/inicio/inicio';
import { MainLayout } from './layout/main-layout/main-layout';

export const routes: Routes = [
  {
    path: '',
    component: Home,
  },
  {
    path: 'login',
    component: Login,
  },
  {
    path: '',
    component: MainLayout,
    children: [
      {
        path: 'inicio',
        component: Inicio,
      },
      {
        path: 'analitica/mapa-calor',
        component: MapaCalor,
      },
      {
        path: 'organizaciones',
        component: OrganizacionesList,
      },
      {
        path: 'organizaciones/nuevo',
        component: OrganizacionNuevo,
      },
      {
        path: 'organizaciones/detalle/:id',
        component: OrganizacionDetalle,
      },
      {
        path: 'organizaciones/:id/editar',
        component: OrganizacionEditar,
      },

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
    ],
  },
];
