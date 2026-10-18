/**
 * Prueba de carga simple sobre la API Tienda (equivalente local a Azure Load Testing).
 *
 * Lanza N peticiones concurrentes durante unos segundos y mide:
 *   - Throughput (peticiones/segundo)
 *   - Latencia p50 y p95 (milisegundos)
 *   - Tasa de error
 * Luego compara contra un SLA y decide PASA / FALLA.
 *
 * Es una version didactica y ligera: Azure Load Testing hace esto a gran escala
 * con Apache JMeter en la nube. Aqui mostramos el CONCEPTO, ejecutable en local
 * con Node puro (sin instalar nada).
 *
 *   Local:      node tests/carga-simple.js
 *   Config:     $env:BASE_URL=...; $env:CONCURRENCIA=20; $env:DURACION_S=8; node tests/carga-simple.js
 *
 * SLA por defecto: p95 < 800 ms y tasa de error < 1%.
 */
const BASE = (process.env.BASE_URL || 'http://localhost:3000').replace(/\/$/, '');
const CONCURRENCIA = Number(process.env.CONCURRENCIA || 10);   // usuarios virtuales
const DURACION_S   = Number(process.env.DURACION_S || 6);      // segundos
const SLA_P95_MS   = Number(process.env.SLA_P95_MS || 800);
const SLA_ERROR_PCT= Number(process.env.SLA_ERROR_PCT || 1);
const RUTA         = process.env.RUTA || '/api/productos';

const c = {
  reset: '\x1b[0m', verde: '\x1b[32m', rojo: '\x1b[31m',
  cyan: '\x1b[36m', gris: '\x1b[90m', bold: '\x1b[1m', amarillo: '\x1b[33m',
};

const latencias = [];
let ok = 0, errores = 0;
let corriendo = true;

async function unaPeticion() {
  const t0 = performance.now();
  try {
    const r = await fetch(BASE + RUTA);
    const dt = performance.now() - t0;
    latencias.push(dt);
    if (r.ok) ok++; else errores++;
    // consumir el body para cerrar la conexion
    await r.text();
  } catch {
    errores++;
    latencias.push(performance.now() - t0);
  }
}

// Un "usuario virtual" hace peticiones en bucle mientras corriendo=true
async function usuarioVirtual() {
  while (corriendo) {
    await unaPeticion();
  }
}

function percentil(arr, p) {
  if (arr.length === 0) return 0;
  const ordenado = [...arr].sort((a, b) => a - b);
  const idx = Math.ceil((p / 100) * ordenado.length) - 1;
  return ordenado[Math.max(0, idx)];
}

async function main() {
  console.log('\n' + c.bold + '=== PRUEBA DE CARGA — API Tienda ===' + c.reset);
  console.log(c.gris + 'Base URL     : ' + BASE + RUTA);
  console.log('Concurrencia : ' + CONCURRENCIA + ' usuarios virtuales');
  console.log('Duracion     : ' + DURACION_S + ' s');
  console.log('SLA          : p95 < ' + SLA_P95_MS + ' ms  y  error < ' + SLA_ERROR_PCT + '%' + c.reset + '\n');

  // Verificar que la app responde antes de empezar
  try {
    const r = await fetch(BASE + '/api/health');
    if (!r.ok) throw new Error('health status ' + r.status);
  } catch (e) {
    console.error(c.rojo + 'La app no responde en ' + BASE + '. Arrancala con: npm start (en app-tienda)' + c.reset + '\n');
    process.exit(1);
  }

  console.log(c.cyan + 'Generando carga...' + c.reset);
  const inicio = performance.now();

  // Lanzar los usuarios virtuales en paralelo
  const usuarios = Array.from({ length: CONCURRENCIA }, () => usuarioVirtual());

  // Detener despues de DURACION_S segundos
  await new Promise(res => setTimeout(res, DURACION_S * 1000));
  corriendo = false;
  await Promise.all(usuarios);

  const segundos = (performance.now() - inicio) / 1000;
  const total = ok + errores;
  const throughput = total / segundos;
  const errorPct = total ? (errores / total) * 100 : 0;
  const p50 = percentil(latencias, 50);
  const p95 = percentil(latencias, 95);

  // ── Reporte ──────────────────────────────────────────────
  console.log('\n' + c.bold + '── RESULTADOS ─────────────────────────────' + c.reset);
  console.log('  Peticiones totales : ' + total);
  console.log('  Exitosas / Errores : ' + c.verde + ok + c.reset + ' / ' + (errores ? c.rojo : c.verde) + errores + c.reset);
  console.log('  Throughput         : ' + throughput.toFixed(1) + ' req/s');
  console.log('  Latencia p50       : ' + p50.toFixed(1) + ' ms');
  console.log('  Latencia p95       : ' + p95.toFixed(1) + ' ms');
  console.log('  Tasa de error      : ' + errorPct.toFixed(2) + ' %');

  // ── Evaluar SLA ──────────────────────────────────────────
  const cumpleP95 = p95 < SLA_P95_MS;
  const cumpleError = errorPct < SLA_ERROR_PCT;
  const pasa = cumpleP95 && cumpleError;

  console.log('\n' + c.bold + '── EVALUACION DEL SLA ─────────────────────' + c.reset);
  console.log('  p95 < ' + SLA_P95_MS + ' ms   : ' + (cumpleP95 ? c.verde + 'CUMPLE' : c.rojo + 'NO CUMPLE') + c.reset + ' (' + p95.toFixed(0) + ' ms)');
  console.log('  error < ' + SLA_ERROR_PCT + '%   : ' + (cumpleError ? c.verde + 'CUMPLE' : c.rojo + 'NO CUMPLE') + c.reset + ' (' + errorPct.toFixed(2) + '%)');

  console.log('\n' + c.bold + '===========================================' + c.reset);
  if (pasa) {
    console.log('  ' + c.verde + c.bold + 'CARGA OK — el rendimiento cumple el SLA' + c.reset);
  } else {
    console.log('  ' + c.rojo + c.bold + 'CARGA FALLIDA — el rendimiento no cumple el SLA' + c.reset);
    console.log('  ' + c.gris + 'En un pipeline, esto seria un quality gate que detiene el deploy.' + c.reset);
  }
  console.log(c.bold + '===========================================' + c.reset + '\n');

  process.exit(pasa ? 0 : 1);
}

main();
