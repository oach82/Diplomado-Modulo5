/**
 * App Tienda - un solo proceso Node/Express que sirve:
 *   - El front estatico (public/) : catalogo, detalle, carrito
 *   - La API REST (/api/...)      : productos, pedidos, health
 *
 * Es la MISMA app que las sesiones usan como laboratorio. Las pruebas E2E
 * del Dia 4 (Playwright + Screenplay + BDD) navegan este front y validan la API.
 *
 * Arranque:  npm start   (http://localhost:3000)
 * Puerto:    $env:PORT=8080; npm start   para cambiarlo
 */
import express from 'express';
import { readFileSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const RAIZ = join(__dirname, '..');
const DB_PATH = join(RAIZ, 'datos', 'db.json');

if (!existsSync(DB_PATH)) {
  console.error('No existe datos/db.json. Ejecuta: npm install (corre postinstall) o node datos/generar-datos.js');
  process.exit(1);
}

const db = JSON.parse(readFileSync(DB_PATH, 'utf-8'));
let productos = db.productos;
let pedidos = db.pedidos || [];
let siguientePedidoId = 1;

const app = express();
app.use(express.json());
app.use(express.static(join(RAIZ, 'public')));

// ── API ────────────────────────────────────────────────────────────
app.get('/api/health', (_req, res) => {
  res.json({ estado: 'ok', hora: new Date().toISOString() });
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

app.get('/api/pedidos', (_req, res) => res.json(pedidos));

// Endpoint de apoyo para pruebas: reinicia los pedidos en memoria
app.post('/api/test/reset', (_req, res) => {
  pedidos = [];
  siguientePedidoId = 1;
  res.json({ ok: true });
});

// Front: cualquier otra ruta devuelve el index (SPA simple)
app.get('*', (_req, res) => {
  res.sendFile(join(RAIZ, 'public', 'index.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log('\n==============================================');
  console.log('  App Tienda corriendo');
  console.log(`  Front : http://localhost:${PORT}/`);
  console.log(`  API   : http://localhost:${PORT}/api/productos`);
  console.log(`  Salud : http://localhost:${PORT}/api/health`);
  console.log('==============================================\n');
});
