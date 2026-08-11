# Módulo de Paquetes, Guías y Manuales

Documentación para integrar el módulo de **paquetes** (productos), **extras** y **guías/manuales** (archivos en base64) en el sistema Cangurera Inteligente.

---

## 1. Base de datos (ejecutar primero)

Correr el script `app_web_net/Paquetes_Clientes.sql` contra la base real (db57112). Es **idempotente** (se puede ejecutar más de una vez).

Cambios que aplica:

| Cambio | Detalle |
|---|---|
| `Operativo.Productos.IncluyeMochila` | `BIT NOT NULL DEFAULT (1)` — indica si el paquete incluye mochila. |
| Tabla `Operativo.ProductoContenido` | Extras del paquete: `IdProductoContenido`, `IdProducto` (paquete), `IdItem` (producto incluido), `Cantidad`. |
| Tabla `Operativo.ProductoDocumento` | Guías/manuales: `IdProductoDocumento`, `IdProducto`, `NombreArchivo`, `TipoContenido` (MIME), `Descripcion`, `ContenidoBase64 NVARCHAR(MAX)`, `FechaSubida`. |
| `Operativo.Ventas.IdOrganizacion` | Venta ligada a la organización compradora (FK → `Operativo.Organizaciones`). |
| `Operativo.Ventas` / `Operativo.DetalleVenta` | Se crean si no existen. |

> El cliente **nunca ve** materia prima, costos, stock ni margen de ganancia: solo información pública.

---

## 2. GUÍA RÁPIDA — ¿Cómo subo una guía/manual? (SIN código)

Los manuales **NO se suben en una página aparte**: se agregan desde el **módulo de PRODUCTOS** (portal admin), editando el producto/paquete correspondiente.

> ⚠️ **Importante:** primero hay que haber ejecutado `Paquetes_Clientes.sql` en la base de datos (ver sección 1). Si la sección "Guías y manuales" no aparece al editar, es que el script no se ha corrido.

### Paso a paso en la web

1. Inicia sesión como **admin**.
2. En el menú lateral ve a **Productos** (listado de productos/paquetes: `http://localhost:4200/productos`).
3. Busca el paquete que quieres (ej. "Mochila Vision Guard Pro") y da clic en **Ver detalles**.
4. En la página de detalle, da clic en **Editar** (o ve directo a `http://localhost:4200/productos/{id}/editar`).
5. Desplázate hasta la sección **"Guías y manuales"** (viene después de "Receta" y "Extras del paquete"):
   - **📎 Elegir archivo** → selecciona el PDF/documento desde tu computadora.
   - (Opcional) Escribe una **Descripción** (ej. "Manual de usuario v2").
   - Clic en **"+ Subir guía/manual"** → espera a que termine (el botón cambia a "Subiendo...").
6. Verás el archivo en la lista de abajo. Si te equivocaste, elimínalo con el botón 🗑.
7. Opcional: en esa misma página puedes marcar/desmarcar **"Incluye mochila"** y agregar **extras** al paquete.

### ¿Y el resto del formato?

Si prefieres ver la pantalla de edición con más detalle, sección "Paquete" + "Extras del paquete" + "Guías y manuales" están todas en `/productos/:id/editar`.

### ¿Qué ve el cliente?

Una vez subido el manual, el cliente lo descarga así: **Mis Compras** → **Ver producto** (en cualquier producto de la compra) → sección **"Guías y manuales"** → botón **⬇ Descargar**.

> Si el cliente entra y **no ve los manuales**: verifica que (a) el script SQL se corrió, (b) el archivo se subió desde Productos → Editar, y (c) el producto fue comprado por la organización del cliente (`mis-productos/:id` solo se abre desde `mis-compras`).

---

## 3. Backend — Endpoints (API)

Todos bajo `api/productos`. Solo el **admin** usa los de escritura.

### Guías y manuales (base64)

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/api/productos/{idProducto}/documentos` | Sube un archivo en base64. Cuerpo: `{ nombreArchivo, tipoContenido, descripcion?, contenidoBase64 }`. |
| `GET` | `/api/productos/documentos/{idDocumento}` | Devuelve el archivo completo para descarga: `{ idProductoDocumento, nombreArchivo, tipoContenido, contenidoBase64 }`. |
| `DELETE` | `/api/productos/documentos/{idDocumento}` | Elimina una guía/manual. |
| `GET` | `/api/productos/{id}/detalle` | Detalle **admin**: incluye `contenido` y `documentos` (metadatos, sin base64) + receta. |
| `GET` | `/api/productos/publico/{id}` | Detalle **cliente**: `incluyeMochila`, `contenido`, `documentos` (metadatos). Sin receta/costos/stock. |

Ejemplo `POST` de manual:

```json
{
  "nombreArchivo": "manual_uso_v2.pdf",
  "tipoContenido": "application/pdf",
  "descripcion": "Manual de uso actualizado",
  "contenidoBase64": "JVBERi0xLjQgLi4u" 
}
```

### Extras del paquete

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/api/productos/{idProducto}/contenido` | Agrega un extra: `{ idItem, cantidad }`. |
| `DELETE` | `/api/productos/{idProducto}/contenido/{idContenido}` | Quita un extra (`idContenido` = `IdProductoContenido`). |

### Ventas (Mis Compras)

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/api/ventas?organizacionId=N` | Ventas de una organización (cliente). |
| `POST` | `/api/ventas` | Registra venta (admin): requiere `{ idOrganizacion, detalles: [{ idProducto, cantidad }] }`; descuenta stock y calcula total. |

---

## 4. Frontend Angular — ¿Dónde se insertan los manuales?

### Página admin: `producto-editar`

Ruta: `/productos/:id/editar` → `src/app/pages/productos/producto-editar/`

Nuevas secciones (después de "Receta"):

- **Paquete** → switch **"Incluye mochila"** (formControl `incluyeMochila`).
- **Extras del paquete** → selector de producto + cantidad, botón "+ Agregar extra", listado con eliminar.
- **Guías y manuales** → botón "📎 Elegir archivo" (input file), campo opcional "Descripción", botón "+ Subir guía/manual". Se convierte a base64 con `FileReader.readAsDataURL` y se guarda con `ProductosService.agregarDocumento()`.

Métodos ya implementados en el componente (`producto-editar.ts`):

```typescript
onArchivoSeleccionado(event)      // guarda el File seleccionado
subirDocumento()                  // lee archivo → base64 → POST /documentos
quitarDocumento(idDocumento)      // DELETE /documentos/{id}
agregarExtra() / quitarExtra(idProductoContenido)
```

### Servicios

- `services/producto.ts` → `agregarDocumento(id, dto)`, `eliminarDocumento(idDoc)`, `descargarDocumento(idDoc)`, `agregarContenido(id, dto)`, `eliminarContenido(id, idContenido)`, `getPublico(id)`.
- `services/ventas.ts` → `getAll(organizacionId?)`, `getById(id)`, `create(dto)`.
- `interfaces/producto.ts` → `ProductoPublico`, `ContenidoDetalle`, `DocumentoArchivo`, `DocumentoCreateDto`.
- `interfaces/venta.ts` → `Venta`, `DetalleVentaItem`, `VentaCreateDto`.

### Vista cliente (solo lectura)

- `/mis-compras` → lista de compras de la organización (tarjetas) → botón "Ver producto".
- `/mis-productos/:id` → detalle del paquete (tarjeta): contenido (mochila + extras) y **guías/manuales descargables** (base64 → Blob → descarga con `atob`).

---

## 5. Cómo crear tu propio módulo de manuales (paso a paso)

Si quieres hacer una página nueva (ej. "Manuales" con su propio listado) en vez de usar la sección de producto-editar, el patrón es:

1. **No crees tablas nuevas**: usa `Operativo.ProductoDocumento` (ya ligada a `Productos` por `IdProducto`).
2. En el backend, reutiliza los endpoints existentes o agrega filtros al `ProductosController`:
   ```csharp
   // Ej: listar documentos de un producto
   [HttpGet("{id:int}/documentos")]
   public async Task<IActionResult> ListarDocumentos(int id, CancellationToken ct)
       => Ok(await db.ProductosDocumento
            .Where(d => d.IdProducto == id)
            .Select(d => new DocumentoDto { ... })   // SIN base64 en listados
            .ToListAsync(ct));
   ```
   > Regla: los listados y detalles **nunca incluyen `ContenidoBase64`**; la descarga usa `GET /api/productos/documentos/{id}`.
3. En Angular:
   - Crea tu página bajo `src/app/pages/mis-modulo/...` con `templateUrl/styleUrl`.
   - Usa `ProductosService` (ya tiene todo) o crea tu servicio `HttpClient` apuntando a `${environment.apiUrl}/api/productos/...`.
   - Para subir: input `type="file"` + `FileReader` → base64 → `agregarDocumento()`.
   - Para descargar: `descargarDocumento(id)` → `atob()` → `Blob` → `a.download` (ver patrón en `pages/cliente/productos/productos.ts`).
4. Registra la ruta en `app.routes.ts` dentro del `MainLayout` y protégelo con `rolGuard(['admin'])` si es admin.
5. Si el módulo es de cliente: **solo `GET`**, y guarda en `rolGuard(['usuario'])`.

---

## 6. Verificación

```bash
# Backend (dentro de backend_net)
dotnet build

# Frontend (dentro de angular_frontendWeb)
npm run build        # o: npx ng build
npx ng test --watch=false
```

Construcción de base64 desde consola (ej. para probar el endpoint):

```bash
base64 -w0 manual.pdf
```

---

## 7. Módulo pendiente: Comentarios de clientes (compañera)

> Este módulo **aún no está implementado**. Le toca a la compañera desarrollarlo.
> Las decisiones de diseño están **abiertas** — abajo van sugerencias marcadas con ✅ (recomendado), pero las define ella.

### Objetivo

El cliente deja una opinión/comentario sobre un **producto** (paquete) desde su vista, y se muestran después en el detalle del producto. Es el siguiente módulo después de Paquetes/Manuales.

### Decisiones abiertas de diseño

| Decisión | Sugerencia |
|---|---|
| Contenido del comentario | ✅ Texto + calificación con estrellas 1-5 (como reseñas de tienda). Alternativa: solo texto o solo estrellas. |
| Quién puede comentar | ✅ Solo clientes de la organización que **compró ese producto** (validar en `DetalleVenta`). Alternativa: cualquier usuario autenticado. |
| Dónde se muestran | ✅ Sección en `/mis-productos/:id` (detalle del paquete, bajo "Guías y manuales"). Opcional: promedio de estrellas en las tarjetas de `/mis-compras`. |
| Admin | Listar y eliminar comentarios desde Productos → Ver detalles → Editar (o una pestaña aparte). |

### Pasos sugeridos (seguir el patrón de este documento)

1. **SQL:** crear un script idempotente nuevo, ej. `Comentarios_Clientes.sql`, con la tabla
   `Operativo.ProductoComentario` (`IdProductoComentario`, `IdProducto`, `IdOrganizacion`, `Comentario NVARCHAR(MAX)`, `Calificacion TINYINT 1-5`, `FechaSubida`).
   > ⚠️ **NO tocar** `Paquetes_Clientes.sql`; cada módulo su script.
2. **Backend:** modelo + `DbSet` + relaciones en `CangureraDbContext.cs`; dos endpoints:
   - `GET /api/productos/{id}/comentarios` — **público** (metadatos + comentario + calificacion; sin datos sensibles de la organización).
   - `POST /api/productos/{id}/comentarios` — cliente; validar que la organización del usuario compró ese producto.
   - `DELETE /api/productos/comentarios/{id}` — admin.
3. **Frontend cliente:** sección de comentarios en `pages/cliente/productos/` (form si aplica + listado con estrellas).
   **Frontend admin:** listado/eliminación en `producto-editar`.
4. **Reglas que NO se pueden romper:**
   - Cliente **solo lectura** y nunca ve receta/materias primas/costos/stock/margen.
   - Rutas protegidas con `rolGuard(['usuario'])` / `rolGuard(['admin'])`.
   - Los listados nunca embeber base64.
   - Correr `dotnet build`, `npx ng build` y `npx ng test --watch=false`; no romper los 9 fallos pre-existentes ajenos (hero/home, dispositivos, organizaciones, app).

---

## 8. Cambios recientes (CSS — vista admin editar producto)

Fix visual aplicado `11/08/2026` en `pages/productos/producto-editar/producto-editar.css`:

- **Se eliminó una regla duplicada** `.form-seccion-titulo:first-of-type { margin-top: 24px; }` (agregada al final del archivo) que ganaba por cascada sobre la original (`margin-top: 0`) y provocaba un hueco extra de 24px sobre el título "Información general" en **todas** las ediciones de producto.
- **Títulos de sección estandarizados:** "Extras del paquete" y "Guías y manuales" usan `.paquete-seccion > .form-seccion-titulo { margin: 24px 0 12px }`, igual al resto del formulario.
- **Filas de extras/manuales:** texto con `ellipsis` (no desborda), botón 🗑 centrado verticalmente con `align-self: auto` en el botón de agregar.
- **Responsive:** `@media (max-width: 640px)` apila los controles de `.paquete-agregar` (selector, cantidad, botón, archivo) a ancho completo; `.archivo-input` con `flex-wrap`.

No se tocó HTML ni TypeScript; solo esta hoja de estilos (variables locales, no afecta otras páginas).

---

## Archivos tocados (resumen)

**Backend:** `Models/ProductoContenido.cs`, `Models/ProductoDocumento.cs`, `Models/Productos.cs`, `Models/Venta.cs`, `Models/CangureraDbContext.cs`, `DTOs/PaqueteDtos.cs`, `DTOs/VentaDtos.cs`, `DTOs/RecetaItemDto.cs`, `Controllers/ProductosController.cs`, `Controllers/VentasController.cs`.

**Frontend:** `interfaces/producto.ts`, `interfaces/venta.ts`, `services/producto.ts`, `services/ventas.ts`, `pages/productos/producto-editar/*` (incluye fix CSS `producto-editar.css`), `pages/cliente/compras/*`, `pages/cliente/productos/*`, `app.routes.ts`, `layout/main-layout/main-layout.ts`.

**SQL:** `app_web_net/Paquetes_Clientes.sql` (ejecutar contra db57112).