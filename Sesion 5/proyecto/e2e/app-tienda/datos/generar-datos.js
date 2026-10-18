/**
 * Genera datos de productos con Faker (semilla fija = reproducible).
 * Coherente con el Dia 1 (datos sinteticos) y el Dia 2 (servicio-tienda).
 * Escribe datos/db.json que el servidor sirve en /api/productos.
 */
import { faker } from '@faker-js/faker';
import { writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// Semilla fija: los datos salen iguales en cada maquina y corrida
faker.seed(12345);

const CATEGORIAS = ['hogar', 'tecnologia', 'ropa', 'juguetes'];
const TOTAL = 24;

const productos = Array.from({ length: TOTAL }, (_, i) => {
  const categoria = CATEGORIAS[i % CATEGORIAS.length];
  return {
    id: i + 1,
    nombre: faker.commerce.productName(),
    categoria,
    precio: Number(faker.commerce.price({ min: 5, max: 500 })),
    descripcion: faker.commerce.productDescription(),
    stock: faker.number.int({ min: 0, max: 50 }),
  };
});

const db = { productos, pedidos: [] };

mkdirSync(__dirname, { recursive: true });
writeFileSync(join(__dirname, 'db.json'), JSON.stringify(db, null, 2), 'utf-8');
console.log(`datos/db.json generado con ${productos.length} productos (semilla fija).`);
