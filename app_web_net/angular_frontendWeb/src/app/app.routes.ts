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
