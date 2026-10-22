/**
 * PROVIDER — API de la Tienda (Dia 6, contract testing con Pact).
 *
 * Expone la API REST que CONSUMEN otros servicios:
 *   GET  /api/health            -> estado
 *   GET  /api/productos         -> lista (filtros: ?categoria= y ?q=)
 *   GET  /api/productos/:id     -> uno (404 si no existe)
 *   POST /api/pedidos           -> crea un pedido
 *
 * En Pact, este servicio es el PROVIDER: cumple el contrato que el CONSUMER
 * (el servicio de notificaciones) espera. Pact verificara que estas respuestas
 * coinciden con lo que el consumer declaro en su contrato.
 *
 * Endpoint extra para Pact (provider states):
 *   POST /api/_pact/state  -> prepara un estado antes de verificar (ver abajo)
 */
import express from 'express';
import { readFileSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const RAIZ = join(__dirname, '..');
const DB_PATH = join(RAIZ, 'datos', 'db.json');

if (!existsSync(DB_PATH)) {
  console.error('No existe datos/db.json. Ejecuta: npm install (postinstall) o node datos/generar-datos.js');
  process.exit(1);
}

const db = JSON.parse(readFileSync(DB_PATH, 'utf-8'));
let productos = db.productos;
let pedidos = [];
let siguientePedidoId = 1;

const app = express();
app.use(express.json());

app.get('/api/health', (_req, res) => {
  res.json({ estado: 'ok', servicio: 'provider-tienda', hora: new Date().toISOString() });
});

app.get('/api/productos', (req, res) => {
  const { categoria, q } = req.query;
  let lista = productos;
  if (categoria) lista = lista.filter((p) => p.categoria === String(categoria).toLowerCase());
  if (q) {
    const t = String(q).toLowerCase();
    lista = lista.filter((p) => p.nombre.toLowerCase().includes(t));
  }
  res.json(lista);
});

app.get('/api/productos/:id', (req, res) => {
  const p = productos.find((x) => x.id === Number(req.params.id));
  if (!p) return res.status(404).json({ error: 'Producto no encontrado' });
  res.json(p);
  /** res.json("valor: precio"); */
});

app.post('/api/pedidos', (req, res) => {
  const { productoId, cliente, cantidad } = req.body || {};
  if (!productoId || !cliente || !cantidad) {
    return res.status(400).json({ error: 'Faltan datos: productoId, cliente, cantidad' });
  }
  const prod = productos.find((x) => x.id === Number(productoId));
  if (!prod) return res.status(404).json({ error: 'Producto no existe' });
  const pedido = {
    id: siguientePedidoId++,
    productoId: Number(productoId),
    cliente,
    cantidad: Number(cantidad),
    total: prod.precio * Number(cantidad),
    estado: 'pendiente',
    creado: new Date().toISOString(),
  };
  pedidos.push(pedido);
  res.status(201).json(pedido);
});

// ── Provider states para Pact ───────────────────────────────────────
// Antes de verificar cada interaccion, Pact puede pedir "pon al provider en
// tal estado". Aqui lo implementamos simple: como los datos son deterministas
// (semilla fija), casi no hace falta, pero dejamos el hook para que la
// verificacion sea robusta y el alumno vea como funciona.
app.post('/api/_pact/state', (req, res) => {
  const { state } = req.body || {};
  console.log(`[pact] provider state solicitado: ${state}`);
  // Ejemplo: si el consumer declaro "existe el producto 1", garantizamos que
  // los datos esten (ya lo estan por la semilla). Aqui podrias resetear/sembrar.
  res.json({ ok: true, state: state || null });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log('\n==============================================');
  console.log('  PROVIDER Tienda corriendo');
  console.log(`  API   : http://localhost:${PORT}/api/productos`);
  console.log(`  Salud : http://localhost:${PORT}/api/health`);
  console.log(`  Productos: ${productos.length}`);
  console.log('==============================================\n');
});
