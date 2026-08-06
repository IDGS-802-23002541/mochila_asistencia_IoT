import { Routes } from '@angular/router';

import { Home } from './pages/home/home';
import { Login } from './pages/login/login';
import { Inicio } from './pages/inicio/inicio';
import { MainLayout } from './layout/main-layout/main-layout';

// Analítica
import { Graficas } from './pages/graficas/graficas';
import { Ajustes } from './pages/ajustes/ajustes';

// Dispositivos
import { ListDispositivo } from './pages/dispositivos/dispositivo-list/list-dispositivo';
import { DispositivoDetalle } from './pages/dispositivos/dispositivo-detalle/detalle-dispositivo';
import { NuevoDispositivo } from './pages/dispositivos/dispositivo-nuevo/nuevo-dispositivo';
import { EditarDispositivo } from './pages/dispositivos/dispositivo-editar/editar-dispositivo';

// Organizaciones
import { OrganizacionDetalle } from './pages/organizaciones/organizacion-detalle/organizacion-detalle';
import { OrganizacionesList } from './pages/organizaciones/organizaciones-list/organizaciones-list';
import { OrganizacionEditar } from './pages/organizaciones/organizacion-editar/organizacion-editar';
import { OrganizacionNuevo } from './pages/organizaciones/organizacion-nuevo/organizacion-nuevo';

// Productos
import { ProductoList } from './pages/productos/producto-list/producto-list';
import { ProductoNuevo } from './pages/productos/producto-nuevo/producto-nuevo';
import { ProductoDetalle } from './pages/productos/producto-detalle/producto-detalle';
import { ProductoEditar } from './pages/productos/producto-editar/producto-editar';

// Proveedores
import { ProveedorList } from './pages/proveedores/proveedor-list/proveedor-list';
import { ProveedorNuevo } from './pages/proveedores/proveedor-nuevo/proveedor-nuevo';
import { ProveedorDetalle } from './pages/proveedores/proveedor-detalle/proveedor-detalle';
import { ProveedorEditar } from './pages/proveedores/proveedor-editar/proveedor-editar';

// Materia prima
import { MateriaPrimaList } from './pages/materiaprima/materiaprima-list/materiaprima-list';
import { MateriaPrimaNuevo } from './pages/materiaprima/materiaprima-nuevo/materiaprima-nuevo';
import { MateriaPrimaDetalle } from './pages/materiaprima/materiaprima-detalle/materiaprima-detalle';
import { MateriaPrimaEditar } from './pages/materiaprima/materiaprima-editar/materiaprima-editar';

// Proteccion rutas
import { authGuard } from './guards/auth.guard';
import { loginGuard } from './guards/login-guard';

export const routes: Routes = [
  {
    path: '',
    component: Home,
  },
  {
    path: 'login',
    component: Login,
    canActivate: [loginGuard]
  },
  {
    path: 'welcome',
    component: Home,
  },
  {
    path: '',
    component: MainLayout,
    canActivate: [authGuard],
    children: [
      {
        path: '',
        redirectTo: 'inicio',
        pathMatch: 'full',
      },
      {
        path: 'inicio',
        component: Inicio
      },

      // Analítica
      {
        path: 'analitica/mapa-calor',
        component: Graficas,
      },
      {
        path: 'graficas/dashboard',
        component: Graficas,
      },
      {
        path: 'graficas',
        component: Graficas,
      },
      {
        path: 'ajustes',
        component: Ajustes,
        canActivate: [authGuard]
      },

      // Dispositivos
      {
        path: 'dispositivos',
        component: ListDispositivo,
      },
      {
        path: 'dispositivos/nuevo',
        component: NuevoDispositivo,
      },
      {
        path: 'dispositivos/detalle/:id',
        component: DispositivoDetalle,
      },
      {
        path: 'dispositivos/:id/editar',
        component: EditarDispositivo,
      },

      // Organizaciones
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

      // Productos
      {
        path: 'productos',
        component: ProductoList,
      },
      {
        path: 'productos/nuevo',
        component: ProductoNuevo,
      },
      {
        path: 'productos/detalle/:id',
        component: ProductoDetalle,
      },
      {
        path: 'productos/:id/editar',
        component: ProductoEditar,
      },

      // Proveedores
      {
        path: 'proveedores',
        component: ProveedorList,
      },
      {
        path: 'proveedores/nuevo',
        component: ProveedorNuevo,
      },
      {
        path: 'proveedores/detalle/:id',
        component: ProveedorDetalle,
      },
      {
        path: 'proveedores/:id/editar',
        component: ProveedorEditar,
      },

      // Materia prima
      {
        path: 'materiaprima',
        component: MateriaPrimaList,
      },
      {
        path: 'materiaprima/nuevo',
        component: MateriaPrimaNuevo,
      },
      {
        path: 'materiaprima/detalle/:id',
        component: MateriaPrimaDetalle,
      },
      {
        path: 'materiaprima/:id/editar',
        component: MateriaPrimaEditar,
      },
    ],
  },
];
