# Dia 5 — DevOps + IA + ejecucion en la nube (Sauce Labs)

Toma el framework del Dia 4 (Playwright + Screenplay + BDD en Python) y lo lleva
a **ejecucion en navegadores reales en la nube** con **Sauce Labs**, integrado a
un **pipeline de Azure**. La clave: **las mismas pruebas** corren en local o en la
nube cambiando solo variables de entorno. El codigo de las pruebas NO cambia.

> Puente con el Dia 4: ya teniamos las pruebas portables por `BASE_URL`. Hoy
> sumamos la portabilidad del NAVEGADOR: local (Chromium) o Sauce (Chrome/Edge
> reales en VMs). Y lo metemos al pipeline.

---

## Que es nuevo frente al Dia 4

| Pieza | Dia 4 | Dia 5 |
|---|---|---|
| Navegador | Chromium local | Local **o** Chrome/Edge reales en Sauce Labs |
| Donde corre | Tu maquina | Tu maquina **y** el pipeline de Azure |
| Seleccion | — | Variables de entorno (`SAUCE=1`) sin tocar el codigo |
| CI/CD | — | `azure-pipelines.yml`: Build -> E2E local -> E2E en Sauce |

---

## Estructura

```
tienda-nube/
├─ app-tienda/            # La app bajo prueba (igual que Dia 4)
├─ screenplay/            # Patron Screenplay (sin cambios)
├─ features/              # Casos en Gherkin (sin cambios)
├─ tests/                 # Steps pytest-bdd (sin cambios)
├─ conftest.py            # NUEVO: actor usa navegador LOCAL o SAUCE segun env
├─ azure-pipelines.yml    # NUEVO: Build -> E2E matriz (chromium/firefox) -> E2E Sauce
├─ tools/triage_ia.py     # NUEVO: triaje de fallos -> prompt para Claude/MCP
├─ .sauce/config.yml      # Referencia de saucectl (Playwright JS)
├─ pytest.ini
└─ requirements.txt       # + pytest-xdist (paralelo) + allure-pytest (reportes)
```

---

## Pre-requisitos

| Herramienta | Version | Para que |
|---|---|---|
| **Node.js** | 18+ (20 recomendado) | correr la app Tienda |
| **Python**  | 3.10+ (probado 3.11) | correr las pruebas |
| **Navegador Playwright** | Chromium | ejecucion local |
| **Cuenta Sauce Labs** | trial/pagada | ejecucion en la nube (demo guiada) |

---

## 1) Correr en LOCAL (igual que el Dia 4)

```powershell
# Terminal 1 — app
cd app-tienda
npm install ; npm start          # http://localhost:3000

# Terminal 2 — pruebas
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m playwright install chromium
pytest
```

Salida esperada: 4 escenarios en verde.

### Multi-navegador (cross-browser) — corre sin cuenta

Playwright trae tres motores: **chromium**, **firefox** y **webkit** (el motor de
Safari). Instalalos y corre la suite en cada uno (un navegador por corrida):

```powershell
python -m playwright install firefox webkit   # chromium ya estaba
pytest --browser chromium
pytest --browser firefox
pytest --browser webkit                        # motor de Safari
```

> Asi se arma una **matriz**: la misma suite validada en varios navegadores. En el
> pipeline esto se hace con una `strategy: matrix` (un job por navegador, en paralelo).

### Paralelismo (mas rapido)

```powershell
pytest -n auto         # usa todos los nucleos (pytest-xdist)
pytest -n 4            # 4 workers
```

### Reportes ricos con Allure

```powershell
pytest --alluredir=resultados/allure          # genera los resultados
# Para ver el reporte HTML necesitas el CLI de Allure (opcional):
#   allure serve resultados/allure
```

### Triaje de fallos asistido por IA (el "+ IA" del dia)

```powershell
pytest --junitxml=resultados/junit.xml        # 1) genera el reporte
python tools/triage_ia.py                     # 2) resume y arma el prompt
```

`tools/triage_ia.py` lee el JUnit, resume pasadas/fallidas y, por cada fallo,
genera un **prompt listo para pegar en Claude** (con el MCP de Playwright) que pide
diagnosticar la causa raiz y proponer un arreglo. El prompt tambien se guarda en
`resultados/triage-prompt.txt` para adjuntarlo en el pipeline.

---

## 2) Correr en la NUBE (Sauce Labs)

La app debe ser **accesible por Sauce** (una URL publica, no `localhost`). Usa la
app desplegada (App Service / App Runner) via `BASE_URL`, o un tunel con Sauce
Connect. Luego define las credenciales y activa Sauce:

```powershell
$env:SAUCE="1"
$env:SAUCE_USERNAME="<tu-usuario>"
$env:SAUCE_ACCESS_KEY="<tu-access-key>"
$env:SAUCE_REGION="us-west-1"          # o eu-central-1
$env:SAUCE_BROWSER="chrome"            # chrome | MicrosoftEdge
$env:SAUCE_PLATFORM="Windows 11"
$env:BASE_URL="https://<tu-app-publica>"
pytest
```

Las credenciales se obtienen en Sauce Labs: **Account -> User Settings** (Username
y Access Key). Al terminar, el dashboard de Sauce muestra cada corrida con video,
logs y capturas.

> Limpia las variables al terminar: `Remove-Item Env:\SAUCE` (o abre una terminal nueva).

---

## 3) Integrar al pipeline de Azure

`azure-pipelines.yml` define tres stages:

1. **Build** — instala la app y las dependencias Python + navegador.
2. **E2E_Local** — arranca la app en el agente y corre `pytest` contra `localhost`;
   publica resultados (JUnit).
3. **E2E_Sauce** — corre las pruebas en Sauce Labs. Solo se activa si existen las
   variables `SAUCE_USERNAME` y `SAUCE_ACCESS_KEY`.

Configura las credenciales como **variables secretas** del pipeline
(Pipelines -> Edit -> Variables), nunca en el YAML en claro. Define tambien
`BASE_URL` con la URL publica de la app.

---

## Como funciona la seleccion local vs nube

En `conftest.py`, el fixture `actor` decide el navegador:

- Sin `SAUCE=1` (o sin credenciales): usa el `page` local de pytest-playwright.
- Con `SAUCE=1` + credenciales: usa `page_sauce`, que conecta Playwright al
  endpoint remoto de Sauce (Chrome/Edge reales en una VM).

El resto del framework (tasks, questions, features) es **identico**. Esa es la
leccion del dia: una suite, muchos entornos.

---

## Notas tecnicas

- **saucectl vs conexion remota:** `saucectl` (`.sauce/config.yml`) es la via
  nativa para Playwright **JS/TS**. Como aqui usamos Playwright for **Python**,
  conectamos al navegador remoto de Sauce desde `conftest.py`. Ambas corren en la
  nube de Sauce; cambia como se lanzan.
- **Honestidad real vs demo:** lo local corre de verdad sin cuenta. Sauce Labs es
  demo guiada (requiere cuenta); el codigo y la config ya estan listos para conectar.
- **Seguridad:** nunca subas `SAUCE_ACCESS_KEY` al repo. Usa variables de entorno
  o secretos del pipeline. El `.gitignore` ya ignora `.env`.
