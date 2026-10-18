# Proyecto Día 3 — Azure DevOps (pipeline + smoke + carga)

Proyecto de la **Sesión 3**. Contiene:

- `azure-pipelines.yml` — el pipeline de Azure DevOps (equivalente al buildspec de AWS).
- `tests/smoke-api.js` — smoke test: confirma que la app responde tras desplegar.
- `tests/carga-simple.js` — prueba de carga con evaluación de SLA (quality gate).

Todo corre **sobre la app Tienda** del pre-requisito (`prerequisito/app-tienda`).

> Los scripts corren en local (Node puro, sin dependencias). El
> `azure-pipelines.yml` es el que se ejecuta en Azure DevOps, pero puedes
> reproducir sus mismos pasos en tu máquina con los comandos de abajo.

---

## Requisitos

- **Node.js 20+**.
- La **app Tienda** corriendo. En otra terminal:
  ```powershell
  cd ..\..\..\prerequisito\app-tienda
  npm install
  npm start            # queda en http://localhost:3000
  ```

---

## 1. Smoke test (¿la app respondió al despliegue?)

Con la app corriendo, en esta carpeta:

```powershell
npm run smoke
```

Valida 7 cosas esenciales: salud, catálogo, producto individual, 404, filtro,
que el front carga y que se puede crear un pedido. Sale con código 0 (OK) o 1 (falla).

Apuntar a una app **desplegada** (App Runner, Azure, etc.):

```powershell
$env:BASE_URL="https://xxxx.awsapprunner.com"; npm run smoke
```

---

## 2. Prueba de carga (¿cumple el SLA?)

```powershell
npm run carga
```

Lanza usuarios virtuales concurrentes durante unos segundos y mide throughput,
latencia p50/p95 y tasa de error. Compara contra el SLA (p95 < 800 ms,
error < 1%) y sale con código 0/1. Es la versión ligera y local del concepto de
**Azure Load Testing**.

Ajustar la intensidad:

```powershell
$env:CONCURRENCIA="20"; $env:DURACION_S="10"; npm run carga
```

---

## 3. Todo junto

```powershell
npm run todo        # smoke + carga
```

---

## 4. El pipeline en Azure DevOps

`azure-pipelines.yml` define 3 stages: **Build → SmokeTests → LoadTest**. Para
usarlo:

1. Sube el repo a Azure Repos o GitHub.
2. En Azure DevOps: **Pipelines → New pipeline → tu repo → Existing YAML file →
   `/azure-pipelines.yml`**.
3. Ejecuta. Cada stage aparece en verde si pasa; si el SLA de carga falla, el
   stage LoadTest se pone en rojo y detiene el pipeline (quality gate).

El paso a paso con capturas está en la presentación y el guión de la sesión.
