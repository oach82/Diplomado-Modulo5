# Pipeline E2E + Sauce Labs — ajustes para replicar

Resultado final verificado: los 4 escenarios E2E corren en un navegador **real**
de Sauce Labs vía túnel y pasan (`tests=4, failures=0`, ~34 s), y los
`test_case_id` viajan al JUnit para actualizar el Test Plan de Azure.

Este documento resume **qué estaba roto, qué se cambió y cómo replicarlo** en
otro proyecto con la misma estructura (`prerequisito/app-tienda` + `e2e/`).

---

## 0. El bug que hacía fallar todo (y despistaba)

Síntoma en Azure: `4 failed ... in 0.14s` y un error truncado `Failed: S...`.

Causa real: **no era Sauce ni la red**. Era un `ScopeMismatch` en `conftest.py`.
El fixture `browser_type_launch_args` de `pytest-playwright` es de
`scope="session"`. Al sobrescribirlo sin indicar scope, quedaba `function`, y
toda la cadena de fixtures del navegador (session-scoped) reventaba en el setup,
**antes** de intentar conectar a Sauce. Por eso fallaba en 0.14 s. El `S...` era
`ScopeMismatch`.

Lección: un fallo instantáneo (centésimas de segundo) casi nunca es de red; es
de recolección/fixtures. Hay que leer el traceback completo (`-rA` o el raw log),
no el resumen truncado.

---

## 1. Conexión a Sauce: el mecanismo correcto

Playwright **no** se conecta a Sauce con una URL `wss://` inventada. Sauce expone
un **Selenium Grid 4** que habla CDP, y Playwright (también en Python) lo entiende
de forma nativa con dos variables de entorno, exportadas **antes** de lanzar el
navegador:

```
SELENIUM_REMOTE_URL          = https://ondemand.<region>.saucelabs.com:443/wd/hub
SELENIUM_REMOTE_CAPABILITIES = {"platformName":"Windows 11","browserName":"chrome",
                                "browserVersion":"latest",
                                "sauce:options":{"username":...,"accessKey":...,
                                                 "devTools":true,"tunnelName":...}}
```

Con eso, un `pytest --headed` normal (fixture `page` estándar) abre un Chrome
real en Sauce. El código de las pruebas no cambia.

Doc: https://docs.saucelabs.com/web-apps/automated-testing/playwright/selenium-grid/

---

## 2. Cambios en `e2e/conftest.py`

| Antes | Después |
|-------|---------|
| Fixture `page_sauce` con `playwright.chromium.connect(cdp_url)` y una URL `wss://.../playwright?caps=...` **inventada**. | Eliminado. Se usa el fixture `page` normal de pytest-playwright. |
| El `actor` elegía `page_sauce` o `page`. | El `actor` siempre usa `page`; la nube se activa por variables de entorno. |
| (no existía) | `_configurar_entorno_sauce()` exporta `SELENIUM_REMOTE_URL` y `SELENIUM_REMOTE_CAPABILITIES` al importar el conftest, si `SAUCE=1` + credenciales. |
| (no existía) | Override de `browser_type_launch_args` con **`scope="session"`** que fuerza `headless:False` en Sauce. **El scope es obligatorio**: sin él, `ScopeMismatch`. |

Fragmento clave (el override que arregló el bug):

```python
@pytest.fixture(scope="session")   # <-- scope OBLIGATORIO (igual que el original)
def browser_type_launch_args(browser_type_launch_args):
    if _usar_sauce():
        return {**browser_type_launch_args, "headless": False}
    return browser_type_launch_args
```

> El mismo conftest está replicado en `dia5/proyecto/tienda-nube/conftest.py`.

---

## 3. Cambios en el túnel (Sauce Connect 5) en el pipeline

Sauce Connect 5 cambió respecto a la v4. Ajustes aplicados en el `azure-pipelines.yml`:

| Tema | Antes (fallaba) | Después (correcto) |
|------|-----------------|--------------------|
| Binario | se buscaba `sauce-connect` | se busca `sc` **o** `sauce-connect` (en v5 es `sc`) |
| Comando | — | `sc run ...` |
| Estado/readiness | `--status-address` (no existe en v5) | `--api-address :9000` + readiness en `/readyz` |
| **localhost** | sin flag → Sauce **bloquea** localhost (modo `deny`) | **`--proxy-localhost allow`** (sin esto, el Chrome remoto no ve la app) |
| Lanzamiento en background | heredaba STDIO → "STDIO streams did not close" | `nohup ... </dev/null > sc.log 2>&1 &` |
| Cierre | `pkill -f sauce-connect` (no mataba nada) | `pkill -f "$SC_BIN"` + `pkill -f 'sc run'` |

El puerto **3000** está en la lista de puertos soportados por `--proxy-localhost`
para dispositivos virtuales, así que **no** hace falta tocar `/etc/hosts`.

---

## 4. Cambios en el paso de pytest (Sauce)

- Se agregó `--headed`: Sauce exige modo headed para grabar video del navegador
  remoto (el conftest también lo fuerza, pero se deja explícito).
- Variables de entorno del paso: `SAUCE=1`, `SAUCE_USERNAME`, `SAUCE_ACCESS_KEY`,
  `SAUCE_REGION`, `SAUCE_BROWSER`, `SAUCE_PLATFORM`, `SAUCE_TUNNEL`, `BASE_URL`,
  `BUILD_TAG`. El `SAUCE_TUNNEL` debe ser **el mismo** que abrió el túnel
  (`tienda-tunnel-$(Build.BuildId)`).

---

## 5. Patrón estructural del pipeline (no cambiar)

- **App + túnel + pytest en el MISMO paso/shell.** Los procesos `&` mueren al
  terminar un paso, y los stages no comparten máquina. Si separas la app en un
  paso y pytest en otro, la app ya no existe cuando corre pytest.
- La app arranca con `nohup node servidor/server.js </dev/null > app.log 2>&1 &`
  y se espera a `GET /api/health` antes de seguir.

---

## 6. Estado consolidado del pipeline

Dos stages en paralelo:

- **`E2E_Local`** — matriz `chromium` + `firefox` en el agente. Publica JUnit,
  artefactos Allure y actualiza el Test Plan (solo chromium).
- **`E2E_Sauce`** — las mismas pruebas en navegador real de Sauce vía túnel.
  Publica JUnit + logs y actualiza el Test Plan. Solo corre si existe el secreto
  `SAUCE_USERNAME` (`condition: ne(variables['SAUCE_USERNAME'], '')`).

Ambos actualizan Azure Test Plans con `tools/publicar_test_plan.py`, usando los
`test_case_id` que el conftest escribe en el JUnit desde los tags `@TC<id>`.

---

## 7. Checklist para replicar en otro proyecto

1. Estructura: `prerequisito/app-tienda/` (app con `/api/health`) y `e2e/`
   (framework pytest-playwright + `requirements.txt`).
2. En `e2e/conftest.py`: copiar `_configurar_entorno_sauce()`, el override de
   `browser_type_launch_args` **con `scope="session"`**, y que el `actor` use el
   fixture `page`.
3. Copiar `azure-pipelines.yml` (ajustar `APP_DIR`, `E2E_DIR`, `TEST_PLAN_ID`,
   `TEST_SUITE_ID`).
4. Secretos del pipeline (Pipelines → Edit → Variables, marcar como *secret*):
   - `SAUCE_USERNAME`, `SAUCE_ACCESS_KEY`
   - `AZURE_DEVOPS_PAT` con scope **Test Management (Read & write)**
5. Confirmar la región de Sauce (`SAUCE_REGION`) y la versión de Sauce Connect
   en la URL de descarga (aquí `5.2.2`).
6. Lanzar. Esperado: túnel "readyz OK", pytest contra Chrome real de Sauce,
   `failures=0`, y Test Cases en verde en el plan.
