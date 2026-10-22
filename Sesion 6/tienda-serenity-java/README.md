# Tienda — Serenity BDD (Java) + Healenium + Pact, todo en contenedores (Podman)

Proyecto integrador del **Día 5 (E2E + self-healing)** y el **Día 6 (contract
testing)**, reescrito en **Java**:

- **E2E**: Serenity BDD + patrón **Screenplay** + **Cucumber** (Gherkin en español).
- **Self-healing**: **Healenium** sobre Selenium WebDriver (Serenity usa Selenium
  por debajo), mediante el servicio **hlm-proxy** (enfoque oficial para Serenity).
  Cuando el `data-testid` de un elemento cambia en la app, Healenium lo re-encuentra
  por similitud del árbol DOM y "sana" el test. NO usa librería en el código.
- **Contract testing**: **Pact JVM** (consumer `notificaciones` + provider
  `tienda-api`), con la interacción `GET /api/productos/1`.
- **Todo en contenedores con Podman**: app, base de datos, backend de Healenium,
  Selenium Grid y los propios tests (Gradle) corren en contenedores.

> Nota: este proyecto NO usa Sauce Labs. La ejecución en nube (Sauce) está en el
> proyecto hermano en Python (`../tienda-nube`). Aquí la ejecución es contra un
> **Selenium Grid propio en contenedores**, que es lo que Healenium necesita.

---

## 1. Prerrequisitos: Podman

Necesitas **Podman** (o Docker; cambia `podman` por `docker`). En este curso
usamos Podman porque es *sin demonio* y *rootless*.

### Instalar y arrancar

| Sistema | Instalación | Arrancar la máquina |
|---------|-------------|---------------------|
| Windows | `winget install RedHat.Podman` (o Podman Desktop) | `podman machine init` y luego `podman machine start` |
| macOS   | `brew install podman` | `podman machine init` y `podman machine start` |
| Linux   | gestor de paquetes (`dnf`/`apt` install podman) | no necesita máquina |

Para `podman compose` puede que necesites el proveedor de compose:
`pip install podman-compose` **o** tener `docker-compose` en el PATH (Podman lo
reutiliza).

### Verificar

```bash
podman --version            # 5.x
podman machine list         # en Windows/macOS: una máquina 'Running'
podman compose version      # el proveedor de compose
```

### Comandos de Podman más usados

```bash
# Imágenes y contenedores
podman build -t mi-imagen ./ruta        # construir imagen desde un Dockerfile
podman images                           # listar imágenes
podman run -d --name c1 -p 3000:3000 mi-imagen   # correr en background + publicar puerto
podman ps                               # contenedores corriendo
podman ps -a                            # todos (incluye detenidos)
podman logs -f c1                       # ver logs en vivo
podman exec -it c1 sh                   # entrar a un contenedor
podman stop c1 ; podman rm c1           # detener y borrar
podman rm -f c1                         # forzar borrado

# Redes (para que los contenedores se vean por nombre)
podman network create mi-red
podman network ls
podman network rm -f mi-red

# Compose (stack completo)
podman compose up -d                    # levantar en background
podman compose ps                       # estado del stack
podman compose logs --tail=50           # logs del stack
podman compose run --rm tests <cmd>     # correr un comando puntual en el servicio 'tests'
podman compose down -v                  # apagar y borrar (incluye volúmenes)

# Limpieza general
podman system prune -f                  # borra lo que no se usa (cuidado)
```

---

## 2. Qué hay dentro

```
tienda-serenity-java/
├── app-tienda/                 # SUT: front + API (Node). También provider Pact.
│   └── Dockerfile
├── src/test/java/com/litethinking/qa/
│   ├── ui/PaginaTienda.java            # Targets (localizadores data-testid)
│   ├── tasks/                          # Screenplay: AbrirLaHome, Filtrar..., Agregar...
│   ├── questions/                      # Screenplay: Contador, Categorias, Productos
│   ├── stepdefinitions/                # steps Cucumber (español) + hooks + ParametrosScreenplay
│   ├── pact/consumer/                  # Pact lado consumer (genera el contrato)
│   ├── pact/provider/                  # Pact lado provider (verifica el contrato)
│   └── RunCucumberE2ETest.java         # runner de los features @e2e
├── src/test/resources/
│   ├── features/                       # catalogo.feature, carrito.feature
│   └── serenity.conf                   # driver=remote → apunta al hlm-proxy
├── podman-compose.yml          # stack: app + postgres + healenium + proxy + grid + tests
├── healenium-db-init/          # init SQL de la BD de Healenium
└── build.gradle                # Serenity, Cucumber, Selenium, Pact (SIN healenium-web)
```

> **Self-healing SIN librería:** el proyecto NO incluye `healenium-web` ni un
> `DriverSource` custom. Serenity apunta su WebDriver remoto al `hlm-proxy`
> (`serenity.conf` + `build.gradle`), y el proxy hace el healing de forma
> transparente. Es el enfoque oficial de Healenium para Serenity.

Servicios del stack (`podman-compose.yml`):

| Servicio | Imagen | Para qué |
|----------|--------|----------|
| `app-tienda` | build local | front + API (SUT y provider Pact) |
| `postgres-hlm` | postgres:15 | base de datos de Healenium (huellas DOM) |
| `selector-imitator` | hlm-selector-imitator:1.6 | sugiere el nuevo localizador (ML) |
| `healenium` | hlm-backend:3.5.1 | backend de self-healing. `FIND_ELEMENTS_AUTO_HEALING=true` |
| `hlm-proxy` | hlm-proxy:2.2.1 | **proxy donde Serenity conecta**; aquí ocurre el healing |
| `selenium-hub` | selenium/hub:4.25.0 | Selenium Grid (hub) |
| `chrome` | selenium/node-chromium:4.25.0 | navegador real headless |
| `tests` | gradle:8.10.2-jdk21 | corre E2E y Pact |

---

## 3. Cómo correr (solo comandos podman)

```bash
# 1) Levantar el stack completo (7 servicios)
podman compose up -d

# 2) E2E con Serenity Screenplay + Healenium
podman compose run --rm tests gradle --no-daemon -DbaseUrl=http://app-tienda:3000 e2e

# 3) Contract testing (consumer genera el contrato, provider lo verifica)
podman compose run --rm tests gradle --no-daemon consumerPact
podman compose run --rm tests gradle --no-daemon providerPact

# 4) Apagar y limpiar (incluye volúmenes)
podman compose down -v
```

Comandos de apoyo:

```bash
podman compose ps                   # estado de los servicios
podman compose logs --tail=50       # logs del stack
podman compose build app-tienda     # reconstruir solo la app (tras cambiar el HTML)
```

Reporte Serenity: tras `e2e`, en `target/site/serenity/` (HTML de página única).

---

## 4. Ejercicio Día 5 — self-healing con Healenium

**Importante entender el escenario:** el self-healing NO se prueba cambiando el
selector en el **test**. Se prueba cambiando el **HTML de la app** (como haría un
dev que renombra un `data-testid`). El test sigue buscando el selector viejo;
Healenium re-encuentra el elemento por similitud del árbol DOM. Si cambiaras el
selector del test a uno nuevo, Healenium no tendría huella de ese selector y NO
podría sanar.

### Paso 0 — Reinicio limpio (ejecútalo SIEMPRE antes de empezar)

Garantiza empezar desde cero: imagen de la app sin HTML roto + base de datos sin
huellas viejas. Sáltate esto y, si una corrida anterior dejó la imagen rota, la
"corrida sana" fallará con `NoSuchElementException`.

```powershell
# Desde dia6/proyecto/tienda-serenity-java/
podman compose down -v                                 # borra huellas viejas de PostgreSQL
# revierte el HTML si quedó roto: selector-categoria -> filtro-categoria, y verifica:
Select-String -Path app-tienda/public/index.html -Pattern 'data-testid="filtro-categoria"'
podman build -t tienda-serenity-java_app-tienda ./app-tienda          # imagen con HTML limpio
podman run --rm tienda-serenity-java_app-tienda cat /app/public/index.html | Select-String "filtro-categoria"
Remove-Item -Recurse -Force .\screenshots -ErrorAction SilentlyContinue
```

### Pasos del ejercicio

1. **Corrida sana (Healenium aprende):** `podman compose up -d` y luego
   `podman compose run --rm tests gradle --no-daemon -DbaseUrl=http://app-tienda:3000 e2e`
   → `tests=3, failures=0`. Healenium guarda la huella DOM de los 7 selectores en
   PostgreSQL. Verifica: `podman exec postgres-hlm psql -U healenium_user -d healenium -t -c "SELECT count(*) FROM healenium.selector;"` → **7**.
   Obligatorio: sin huella no hay con qué comparar.
2. **Rompe el HTML de la app:** en `app-tienda/public/index.html`, en el `<select>`
   del filtro, cambia `data-testid="filtro-categoria"` por
   `data-testid="selector-categoria"`. El `id` y la estructura quedan igual.
3. **Reconstruye la imagen y RECREA el contenedor de la app:**
   ```powershell
   podman compose build app-tienda      # imagen con el HTML roto
   podman rm -f tests                    # 'tests' depende de app-tienda (depends_on): borrarlo primero
   podman rm -f app-tienda               # recrear, no reusar
   podman compose up -d app-tienda
   podman exec app-tienda wget -qO- http://localhost:3000/ | Select-String "selector-categoria"  # ✔ debe aparecer
   ```
   **Ojo:** `podman compose up -d app-tienda` a secas *reusa* el contenedor viejo y
   la app seguiría sirviendo el HTML original (pista: `Status = Up 15 minutes` en vez
   de `Up 10 seconds`). Y Podman no deja borrar `app-tienda` sin borrar antes `tests`
   (dependencia `depends_on`). Por eso se borran los dos y se recrea.
4. **Corrida con el cambio (Healenium sana):**
   `podman compose run --rm tests gradle --no-daemon --rerun-tasks -DbaseUrl=http://app-tienda:3000 e2e`
   → **siguen `tests=3, failures=0`** y `4 actionable tasks: 4 executed`. El test busca
   `filtro-categoria` (ya no existe) y Healenium encuentra el `<select>` por similitud, sana el test.
   **Clave — `--rerun-tasks`:** sin esa bandera Gradle marca `e2e` como `UP-TO-DATE`,
   no reabre el navegador y NO hay healing (verde falso, `healing_result` en 0 filas).
5. Revierte el HTML (`selector-categoria` → `filtro-categoria`), reconstruye y
   baja el stack: `podman compose down -v`.

### Ver el reporte de Healenium (la evidencia)

La tabla `healenium.healing_result` registra cada sanación:

```bash
podman exec postgres-hlm psql -U healenium_user -d healenium \
  -c "SELECT (locator::json->>'value') AS localizador_sanado, score, success_healing \
      FROM healenium.healing_result ORDER BY create_date DESC;"
```

Resultado real verificado tras el paso 4:

| localizador_sanado | score | success_healing |
|--------------------|-------|-----------------|
| `select#filtro-categoria` | 0.964 (96.4%) | true |

Healenium detectó que `[data-testid='filtro-categoria']` ya no existía, encontró
el `<select>` por su estructura DOM (usando el `id` que seguía igual) con 96.4%
de similitud y sanó el test. El `SCORE_CAP` del proxy es 0.6: por debajo de 60%
de similitud NO sana (evita falsos positivos). También hay un reporte HTML en
`report/` dentro del contenedor de tests.

### Comparar SIN self-healing

En `build.gradle`, la tarea `e2e` usa `HLM_PROXY_URL` si está, o el grid directo
si no. Para correr sin healing y ver el fallo real, apunta al grid directo
(define `SELENIUM_GRID_URL` sin `HLM_PROXY_URL`): el test falla con
*NoSuchElementException*. Ese contraste es el valor de Healenium.

---

## 5. Ejercicio Día 6 — romper y reparar el contrato (Pact)

1. `podman compose run --rm tests gradle --no-daemon consumerPact` y luego
   `... providerPact` → el provider lo verifica: **BUILD SUCCESSFUL**.
2. "Rompe" la API: en `app-tienda/servidor/server.js`, en `GET /api/productos/:id`,
   devuelve `valor` en vez de `precio`. Reconstruye la app:
   `podman compose build app-tienda && podman compose up -d app-tienda`.
3. `podman compose run --rm tests gradle --no-daemon providerPact` → ahora **FALLA**:
   el provider ya no cumple lo que el consumer declaró (el contrato atrapó la ruptura).
4. Revierte el cambio, reconstruye la app y vuelve a `providerPact`: **verde** otra vez.

---

## 6. Versiones

Java 21 (contenedor `gradle:8.10.2-jdk21`), Gradle 8.10.2, Serenity BDD 4.2.14,
Selenium 4.25.0, Cucumber 7.20.1, Healenium **`hlm-backend:3.5.1`** (tag correcto;
3.5.5 no existe en Docker Hub), `hlm-selector-imitator:1.6`, Pact JVM 4.6.14.

> El wrapper está fijado a Gradle 8.10.2 a propósito: Gradle 9.x rompe el plugin
> de Serenity. Dentro del contenedor usamos `gradle` (de la imagen), que ya es
> 8.10.2.

## 7. Notas técnicas (para reproducir sin sorpresas)

- **Enfoque hlm-proxy (NO librería):** el self-healing con Serenity usa el servicio
  `hlm-proxy`, no la librería `healenium-web`. Serenity apunta su WebDriver remoto
  al proxy (`http://hlm-proxy:8085/wd/hub`). Intentar envolver el driver con
  `SelfHealingDriver.create()` de `healenium-web` es frágil con Serenity (su capa
  `WebElementFacade` intercepta el fallo antes que la librería).

- **`FIND_ELEMENTS_AUTO_HEALING=true` es obligatorio:** Serenity resuelve los Targets
  con `findElements` (plural). Healenium desactiva el healing de búsquedas plurales
  por defecto. Sin este flag en el backend, el self-healing NO ocurre (lo confirmamos:
  el test fallaba con `NoSuchElement` sin que el proxy intentara sanar).

- **El escenario correcto es cambiar la APP, no el test:** Healenium sana cuando el
  MISMO selector que aprendió deja de encontrar su elemento (porque el DOM cambió).
  Si cambias el selector del test a uno nuevo, no hay huella de ese selector y no
  puede sanar ("There is no reference data to selector in the database").

- **Parameter type `{actor}` en Cucumber**: Serenity Screenplay requiere registrar
  el tipo `actor` manualmente con `@ParameterType`. Está en
  `stepdefinitions/ParametrosScreenplay.java`.

- **`@Cuando` y `@Y` no se duplican**: en Cucumber moderno, una anotación
  `@Cuando("...")` cubre también los pasos `Y` que siguen. Tener `@Cuando` y `@Y`
  con el mismo patrón en el mismo método lanza `DuplicateStepDefinitionException`.

- **Bind mount de Podman en Windows**: para corridas largas dentro de contenedores,
  el bind mount (`-v $PWD:/work`) puede dar `Input/output error` si hay locks del
  sistema de archivos. La solución: copiar el código al contenedor con `podman cp`
  y correr desde el sistema de archivos Linux interno.

- **`podman compose` en Windows falla con "could not find a matching machine"**:
  ocurre cuando la máquina Podman (WSL) se reinició y la conexión guardada quedó
  apuntando a un puerto SSH viejo. `podman run`/`podman exec` siguen funcionando, pero
  `podman compose` no. Fix: reinicia la máquina para regenerar la conexión:
  ```
  wsl.exe --terminate podman-machine-default
  podman machine start
  ```

## 8. Resultado verificado end-to-end

Verificado con Podman 5.7.1 en Windows:

| Qué | Resultado |
|-----|-----------|
| `compileTestJava` | BUILD SUCCESSFUL |
| `consumerPact` | BUILD SUCCESSFUL — contrato generado (`spec 3.0.0`) |
| `providerPact` | BUILD SUCCESSFUL — `tests=1 failures=0` |
| `e2e` corrida sana (Serenity + Grid) | BUILD SUCCESSFUL — `tests=3 failures=0` |
| Healenium aprendió | 7 selectores en PostgreSQL (tabla `selector`) |
| `e2e` tras cambiar el `data-testid` en la app | BUILD SUCCESSFUL — `tests=3 failures=0` (¡sanó!) |
| Sanación registrada | `healing_result`: `select#filtro-categoria`, score 0.964, success=true |
