"""Configuracion compartida de pytest para las pruebas E2E (Dia 5).

Novedad del Dia 5: las MISMAS pruebas pueden correr en LOCAL o en la NUBE
(Sauce Labs) solo con variables de entorno. El codigo de las pruebas NO cambia.

Fixtures:
  - base_url : URL de la app bajo prueba (local por defecto, configurable con BASE_URL)
  - actor    : un Actor Screenplay con la habilidad de navegar (local o Sauce)

Ejecucion local (por defecto):
    pytest

Ejecucion en Sauce Labs (nube):  define estas variables y corre pytest --headed
    SAUCE=1
    SAUCE_USERNAME=<tu-usuario>
    SAUCE_ACCESS_KEY=<tu-access-key>
    SAUCE_REGION=us-west-1            # o eu-central-1 (opcional)
    SAUCE_BROWSER=chrome              # chrome | MicrosoftEdge (opcional)
    SAUCE_PLATFORM="Windows 11"       # SO del navegador real (opcional)
    SAUCE_TUNNEL=<nombre-del-tunel>   # si la app no es publica (opcional)

Como conecta a Sauce (sin inventar URLs): el conftest exporta las variables
SELENIUM_REMOTE_URL y SELENIUM_REMOTE_CAPABILITIES que Playwright entiende de
forma nativa (Selenium Grid 4 + CDP). Ver docstring de _configurar_entorno_sauce.

Nota honesta: la ejecucion en Sauce requiere cuenta (trial o pagada). Si no
hay credenciales, todo corre en local sin cambios. En clase, la parte Sauce es
demo guiada con la configuracion ya lista.
"""
import os
import sys
from pathlib import Path

import pytest
import requests

sys.path.insert(0, str(Path(__file__).parent))

from screenplay.actor import Actor
from screenplay.abilities import NavegarConElNavegador


def _usar_sauce() -> bool:
    """True si pedimos ejecutar en Sauce y hay credenciales."""
    return os.environ.get("SAUCE") == "1" and bool(
        os.environ.get("SAUCE_USERNAME") and os.environ.get("SAUCE_ACCESS_KEY")
    )


def pytest_addoption(parser):
    parser.addoption(
        "--base-url-tienda",
        action="store",
        default=None,
        help="URL base de la app Tienda (ej. http://localhost:3000)",
    )


@pytest.fixture(scope="session")
def base_url(request):
    # Prioridad: flag de linea de comandos > variable de entorno > local
    return (
        request.config.getoption("--base-url-tienda")
        or os.environ.get("BASE_URL")
        or "http://localhost:3000"
    )


@pytest.fixture(autouse=True)
def _reset_pedidos(base_url):
    """Deja los pedidos en limpio antes de cada escenario (si la app lo soporta)."""
    try:
        requests.post(f"{base_url}/api/test/reset", timeout=3)
    except requests.RequestException:
        pass
    yield


# ──────────────────────────────────────────────────────────────────
#  Enlace con Azure Test Plans (igual que el Dia 4): el tag @TC<id> del
#  escenario viaja al JUnit como propiedad test_case_id. El pipeline, con
#  tools/publicar_test_plan.py, usa ese ID para marcar el Test Case
#  Passed/Failed en el plan. Asi, si un cambio rompe un test, el Test Plan
#  lo reporta en rojo automaticamente.
# ──────────────────────────────────────────────────────────────────
import re as _re

_TC_RE = _re.compile(r"^TC(\d+)$", _re.IGNORECASE)


def _extraer_test_case_id(tags):
    for t in tags or []:
        m = _TC_RE.match(str(t))
        if m:
            return m.group(1)
    return None


def pytest_bdd_before_scenario(request, feature, scenario):
    """Antes de cada escenario: si tiene tag @TC<id>, lo registra en el JUnit."""
    tc_id = _extraer_test_case_id(getattr(scenario, "tags", None))
    if not tc_id:
        return
    try:
        record_property = request.getfixturevalue("record_property")
        record_property("test_case_id", tc_id)
    except Exception:
        pass


# ──────────────────────────────────────────────────────────────────
#  CONEXION A SAUCE LABS (mecanismo OFICIAL de Playwright: Selenium Grid)
#
#  Playwright no se conecta a Sauce con una URL "wss://" inventada. Sauce
#  expone un Selenium Grid 4 que habla el Chrome DevTools Protocol (CDP), y
#  Playwright lo entiende de forma NATIVA cuando defines dos variables de
#  entorno ANTES de lanzar el navegador:
#
#     SELENIUM_REMOTE_URL           = https://ondemand.<region>.saucelabs.com:443/wd/hub
#     SELENIUM_REMOTE_CAPABILITIES  = {"platformName":..., "browserName":...,
#                                      "sauce:options":{username, accessKey, ...}}
#
#  Con eso, un simple playwright.chromium.launch() abre un Chrome REAL en una
#  VM de Sauce. El codigo de las pruebas NO cambia.
#  Doc oficial: https://docs.saucelabs.com/web-apps/automated-testing/playwright/selenium-grid/
# ──────────────────────────────────────────────────────────────────
def _configurar_entorno_sauce():
    """Exporta SELENIUM_REMOTE_URL y SELENIUM_REMOTE_CAPABILITIES.

    Idempotente: si ya estan definidas, las respeta. Debe llamarse ANTES de
    que pytest-playwright lance el navegador (por eso corre al colectar).
    """
    import json

    region = os.environ.get("SAUCE_REGION", "us-west-1")
    user = os.environ["SAUCE_USERNAME"]
    key = os.environ["SAUCE_ACCESS_KEY"]
    browser_name = os.environ.get("SAUCE_BROWSER", "chrome")
    platform = os.environ.get("SAUCE_PLATFORM", "Windows 11")

    sauce_options = {
        "username": user,
        "accessKey": key,
        "name": os.environ.get("SAUCE_TEST_NAME", "Tienda E2E - Dia 5"),
        "build": os.environ.get("BUILD_TAG", "tienda-e2e-local"),
        # devTools:true es lo que habilita el canal CDP que Playwright necesita.
        "devTools": True,
    }
    # Si la app NO es publica (corre en el agente del pipeline), Sauce la
    # alcanza por el tunel de Sauce Connect. El nombre debe coincidir con el
    # que abrio el pipeline (SAUCE_TUNNEL / --tunnel-name).
    tunnel = os.environ.get("SAUCE_TUNNEL")
    if tunnel:
        sauce_options["tunnelName"] = tunnel

    capabilities = {
        "platformName": platform,
        "browserName": browser_name,
        "browserVersion": os.environ.get("SAUCE_BROWSER_VERSION", "latest"),
        "sauce:options": sauce_options,
    }

    os.environ.setdefault(
        "SELENIUM_REMOTE_URL",
        f"https://ondemand.{region}.saucelabs.com:443/wd/hub",
    )
    os.environ["SELENIUM_REMOTE_CAPABILITIES"] = json.dumps(capabilities)


# Si vamos a correr en Sauce, dejamos el entorno listo al importar el conftest,
# antes de que pytest-playwright construya el navegador.
if _usar_sauce():
    _configurar_entorno_sauce()


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Sauce exige modo HEADED para grabar video. En local no forzamos nada.

    IMPORTANTE: debe declararse con scope='session' igual que el fixture
    original de pytest-playwright. Si se deja en el scope por defecto
    (function), pytest lanza ScopeMismatch al resolver la cadena de fixtures
    del navegador (que es toda de scope session).
    """
    if _usar_sauce():
        return {**browser_type_launch_args, "headless": False}
    return browser_type_launch_args


@pytest.fixture
def actor(request, base_url) -> Actor:
    """Un actor llamado Ana que navega con el navegador adecuado.

    - Si SAUCE=1 y hay credenciales -> el fixture `page` de pytest-playwright ya
      viene conectado al navegador REAL en Sauce (gracias a SELENIUM_REMOTE_URL /
      SELENIUM_REMOTE_CAPABILITIES que exportamos arriba).
    - En caso contrario -> usa el navegador LOCAL.

    En ambos casos usamos el MISMO fixture `page`: el codigo de las pruebas no
    distingue local de nube.
    """
    pagina = request.getfixturevalue("page")
    return Actor.llamado("Ana").que_puede(
        NavegarConElNavegador.usando(pagina, base_url)
    )
