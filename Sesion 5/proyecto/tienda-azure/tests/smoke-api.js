/**
 * Smoke test de la API de la app Tienda.
 *
 * "Smoke test" = pruebas rapidas que confirman que lo esencial funciona
 * DESPUES de un despliegue. No prueban todo: prueban que la app "encendio"
 * y responde. Es lo primero que corre un pipeline tras desplegar.
 *
 * Apunta a la URL que le des en BASE_URL. Sirve para local o para la app
 * desplegada (App Runner, Azure, etc.):
 *
 *   Local:      $env:BASE_URL="http://localhost:3000"; node tests/smoke-api.js
 *   Desplegada: $env:BASE_URL="https://xxxx.awsapprunner.com"; node tests/smoke-api.js
 *
 * Si no defines BASE_URL, usa http://localhost:3000 por defecto.
 * Sale con codigo 0 si todo pasa, 1 si algo falla (para que el pipeline lo lea).
 */
const BASE = (process.env.BASE_URL || 'http://localhost:3000').replace(/\/$/, '');

// Colores para consola
const c = {
  reset: '\x1b[0m', verde: '\x1b[32m', rojo: '\x1b[31m',
  cyan: '\x1b[36m', gris: '\x1b[90m', bold: '\x1b[1m',
};
let pasadas = 0, falladas = 0;

async function check(nombre, fn) {
  try {
    await fn();
    console.log('  ' + c.verde + 'OK ' + c.reset + nombre);
    pasadas++;
  } catch (e) {
    console.log('  ' + c.rojo + 'FALLO ' + c.reset + nombre + c.gris + '  -> ' + e.message + c.reset);
    falladas++;
  }
}

function assert(cond, msg) {
  if (!cond) throw new Error(msg);
}

async function main() {
  console.log('\n' + c.bold + '=== SMOKE TEST — API Tienda ===' + c.reset);
  console.log(c.gris + 'Base URL: ' + BASE + c.reset + '\n');

  // 1) Salud del servicio
  await check('GET /api/health responde 200 y estado ok', async () => {
    const r = await fetch(BASE + '/api/health');
    assert(r.status === 200, 'esperaba 200, llego ' + r.status);
    const j = await r.json();
    assert(j.estado === 'ok', 'estado no es ok: ' + JSON.stringify(j));
  });

  // 2) Catalogo devuelve productos
  await check('GET /api/productos devuelve una lista con productos', async () => {
    const r = await fetch(BASE + '/api/productos');
    assert(r.status === 200, 'esperaba 200, llego ' + r.status);
    const j = await r.json();
    assert(Array.isArray(j), 'la respuesta no es un array');
    assert(j.length > 0, 'el catalogo esta vacio');
  });

  // 3) Un producto individual tiene los campos esperados
  await check('GET /api/productos/1 tiene id, nombre y precio', async () => {
    const r = await fetch(BASE + '/api/productos/1');
    assert(r.status === 200, 'esperaba 200, llego ' + r.status);
    const p = await r.json();
    assert(p.id === 1, 'id incorrecto');
    assert(typeof p.nombre === 'string' && p.nombre.length > 0, 'nombre vacio');
    assert(typeof p.precio === 'number', 'precio no es numero');
  });

  // 4) Producto inexistente -> 404
  await check('GET /api/productos/9999 responde 404', async () => {
    const r = await fetch(BASE + '/api/productos/9999');
    assert(r.status === 404, 'esperaba 404, llego ' + r.status);
  });

  // 5) Filtro por categoria funciona
  await check('GET /api/productos?categoria=hogar devuelve solo esa categoria', async () => {
    const r = await fetch(BASE + '/api/productos?categoria=hogar');
    const j = await r.json();
    assert(j.every(p => p.categoria === 'hogar'), 'hay productos de otra categoria');
  });

  // 6) El front carga (home)
  await check('GET / (front) responde 200 y es HTML', async () => {
    const r = await fetch(BASE + '/');
    assert(r.status === 200, 'esperaba 200, llego ' + r.status);
    const html = await r.text();
    assert(html.includes('Tienda QA'), 'el HTML no parece el de la tienda');
  });

  // 7) Crear un pedido valido -> 201
  await check('POST /api/pedidos con datos validos responde 201', async () => {
    const r = await fetch(BASE + '/api/pedidos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ productoId: 1, cliente: 'smoke@test.com', cantidad: 1 }),
    });
    assert(r.status === 201, 'esperaba 201, llego ' + r.status);
    const p = await r.json();
    assert(p.estado === 'pendiente', 'el pedido no nace pendiente');
  });

  // ── Resumen ──────────────────────────────────────────────
  console.log('\n' + c.bold + '========================================' + c.reset);
  console.log('  Pasadas: ' + c.verde + pasadas + c.reset + '   Falladas: ' + (falladas ? c.rojo : c.verde) + falladas + c.reset);
  if (falladas === 0) {
    console.log('  ' + c.verde + c.bold + 'SMOKE TEST OK — la app respondio bien al despliegue' + c.reset);
  } else {
    console.log('  ' + c.rojo + c.bold + 'SMOKE TEST FALLIDO — el pipeline deberia detener el deploy' + c.reset);
  }
  console.log(c.bold + '========================================' + c.reset + '\n');

  process.exit(falladas === 0 ? 0 : 1);
}

main().catch(e => {
  console.error('\n' + c.rojo + 'No se pudo ejecutar el smoke test: ' + e.message + c.reset);
  console.error(c.gris + '¿Esta la app corriendo en ' + BASE + '? Arrancala con: npm start (en app-tienda)' + c.reset + '\n');
  process.exit(1);
});
