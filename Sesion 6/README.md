# Día 6 — Contenedores y Contract Testing (Podman + Pact)

Proyecto ejecutable del Día 6. Empaquetamos la API de la Tienda en un contenedor
y validamos, con **Pact**, que cumple el **contrato** que espera otro servicio
(notificaciones). Todo corre **dentro de contenedores**.

## Por qué todo en contenedores

`pact-python` trae un Ruby embebido que **no instala bien en Windows local**
(choca con el límite de rutas largas). Por eso el contract testing corre en
contenedores Linux. No es un parche: es exactamente como corre en un pipeline
real, y además deja el entorno reproducible.

Usamos **Podman** en todos los ejemplos (sin demonio, rootless). Los `Dockerfile`
son estándar OCI, así que las imágenes construidas aquí son portables a cualquier
runtime compatible; pero el flujo documentado corre con `podman`.

## Estructura

```
dia6/proyecto/
├── provider-tienda/          # PROVIDER: la API de la Tienda (Node 20)
│   ├── servidor/server.js    #   GET /api/productos, /api/productos/:id, POST /api/pedidos, /api/health
│   ├── datos/generar-datos.js#   Faker con semilla fija (datos deterministas)
│   └── Dockerfile
├── consumer-notificaciones/  # CONSUMER: servicio que usa la API (Python 3.11)
│   ├── cliente_productos.py  #   cliente HTTP + lógica de notificación
│   ├── test_consumer_pact.py #   declara el contrato (consumer-driven)
│   └── Dockerfile            #   corre pytest → ESCRIBE el contrato en /pacts
├── provider-verify/          # Verifica el contrato contra el provider real
│   ├── verificar_provider.py #   Verifier.verify_pacts(...)
│   └── Dockerfile
└── pacts/                    # Contrato generado (volumen compartido)
    └── notificaciones-tienda-api.json
```

## Cómo correr el flujo completo (comandos podman, paso a paso)

> ### 📂 ¿Desde qué carpeta? (importante — hay varias subcarpetas)
>
> Para **Pact Python** te paras **EN `dia6/proyecto/`** (la carpeta que contiene
> `consumer-notificaciones/`, `provider-tienda/`, `provider-verify/` y `pacts/`).
> **NO entres** a esas subcarpetas: te quedas en `proyecto/` y los comandos las
> referencian con `./consumer-notificaciones`, `./provider-tienda`, etc.
>
> ```
> cd dia6/proyecto          ← AQUÍ te paras (no dentro de las subcarpetas)
> # ✔ correcto:  podman build -t consumer-notificaciones ./consumer-notificaciones
> # ✘ incorrecto: cd consumer-notificaciones  (NO entres aquí)
> ```
>
> ¿Por qué en la raíz? Porque el volumen `-v "${PWD}/pacts:/pacts"` necesita que
> `pacts/` esté dentro de tu carpeta actual, y las imágenes se construyen apuntando
> a cada subcarpeta con `./nombre`. Si entras a una subcarpeta, los `./...` y el
> `${PWD}/pacts` dejan de resolver.
>
> **Pact Java es la excepción:** esa vía SÍ se ejecuta DENTRO de la subcarpeta
> `dia6/proyecto/tienda-serenity-java/` (ver su propio README). Regla rápida:
> - Comando con `./consumer-notificaciones` / `./provider-tienda` → párate en `dia6/proyecto/`.
> - Comando con `tienda-tests gradle ... Pact` → párate en `tienda-serenity-java/`.

En PowerShell (Windows) usa `${PWD}` en lugar de `$PWD` para los volúmenes.

```bash
# 0) Red compartida
podman network create pact-net

# 1) CONSUMER genera el contrato en ./pacts
podman build -t consumer-notificaciones ./consumer-notificaciones
podman run --rm -v "$PWD/pacts:/pacts" -e PACT_DIR=/pacts consumer-notificaciones

# 2) PROVIDER real en la red
podman build -t provider-tienda ./provider-tienda
podman run -d --name provider-tienda --network pact-net provider-tienda

# 3) VERIFY valida el contrato contra el provider real
podman build -t provider-verify ./provider-verify
podman run --rm --network pact-net -v "$PWD/pacts:/pacts" \
  -e PROVIDER_URL=http://provider-tienda:3000 \
  -e PACT_FILE=/pacts/notificaciones-tienda-api.json provider-verify

# 4) Limpieza
podman rm -f provider-tienda && podman network rm pact-net
```

En PowerShell (Windows), los pasos 1 y 3 usan `${PWD}`:
```powershell
podman run --rm -v "${PWD}/pacts:/pacts" -e PACT_DIR=/pacts consumer-notificaciones
```

Resultado esperado: **`1 interaction, 0 failures`** y el mensaje
*"el provider CUMPLE el contrato del consumer"*.

## Ejercicio: romper y reparar el contrato

1. Corre el flujo completo → `0 failures`.
2. En `provider-tienda/servidor/server.js`, en `GET /api/productos/:id`,
   renombra `precio` por `valor` en la respuesta.
3. Reconstruye el provider y vuelve a verificar → **falla** (`1 failure`): el
   provider ya no cumple lo que el consumer espera.
4. Revierte el cambio, reconstruye y verifica → vuelve a `0 failures`.

Eso es contract testing atrapando una ruptura de API **antes** de llegar a
producción y romper al consumer.

## Qué corre de verdad

| Pieza                | Herramienta                | ¿Real? |
|----------------------|----------------------------|--------|
| Contenedores         | Podman (OCI, rootless)     | Sí |
| Provider             | API Tienda (Node 20)       | Sí |
| Consumer + test      | Notificaciones (Python)    | Sí |
| Contract testing     | Pact (consumer-driven)     | Sí |
| Orquestación         | Red + volumen de contenedor| Sí |
| Kubernetes           | Deployment / Service / Pod | Conceptual + demo |

## Datos deterministas (semilla fija)

El provider genera sus datos con Faker y **semilla 12345**, así el producto 1 es
siempre el mismo. El contrato declara esa forma:

```json
{ "id": 1, "nombre": "Tasty Concrete Chair", "categoria": "hogar",
  "precio": 106.25, "stock": 5 }
```

Pact valida la **forma** (tipos) con `matchingRules: { "match": "type" }`, no los
valores exactos. Un cambio de datos NO rompe el contrato; solo lo rompe un
cambio de estructura (renombrar/quitar un campo o cambiar su tipo).
