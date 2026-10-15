"""Configuracion compartida de pytest para las pruebas E2E (Dia 5).

Novedad del Dia 5: las MISMAS pruebas pueden correr en LOCAL o en la NUBE
(Sauce Labs) solo con variables de entorno. El codigo de las pruebas NO cambia.

Fixtures:
  - base_url : URL de la app bajo prueba (local por defecto, configurable con BASE_URL)
  - actor    : un Actor Screenplay con la habilidad de navegar (local o Sauce)

Ejecucion local (por defecto):
    pytest

Ejecucion en Sauce Labs (nube):  define estas variables y corre pytest
    SAUCE=1
    SAUCE_USERNAME=<tu-usuario>
    SAUCE_ACCESS_KEY=<tu-access-key>
    SAUCE_REGION=us-west-1            # o eu-central-1 (opcional)
    SAUCE_BROWSER=chrome              # chrome | MicrosoftEdge (opcional)
    SAUCE_PLATFORM="Windows 11"       # SO del navegador real (opcional)

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
#  PAGE: local (pytest-playwright) o remota en Sauce Labs
# ──────────────────────────────────────────────────────────────────
@pytest.fixture
def page_sauce(playwright):
    """Pagina conectada a un navegador REAL en la nube de Sauce Labs.

    Playwright se conecta al endpoint remoto de Sauce via CDP. El navegador
    (Chrome/Edge) corre en una VM real de Sauce; nuestras pruebas lo manejan
    igual que si fuera local.
    """
    region = os.environ.get("SAUCE_REGION", "us-west-1")
    user = os.environ["SAUCE_USERNAME"]
    key = os.environ["SAUCE_ACCESS_KEY"]
    browser_name = os.environ.get("SAUCE_BROWSER", "chrome")
    platform = os.environ.get("SAUCE_PLATFORM", "Windows 11")

    # Endpoint CDP de Sauce para Playwright (segun region)
    host = "us-west-1.saucelabs.com" if region == "us-west-1" else f"{region}.saucelabs.com"
    sauce_options = {
        "username": user,
        "accessKey": key,
        "name": "Tienda E2E - Dia 5",
        "build": os.environ.get("BUILD_TAG", "tienda-e2e-local"),
    }
    # Si la app NO es publica, Sauce la alcanza por un tunel (Sauce Connect).
    # El nombre del tunel debe coincidir con el que abrio el pipeline.
    tunnel = os.environ.get("SAUCE_TUNNEL")
    if tunnel:
        sauce_options["tunnelName"] = tunnel
    capabilities = {
        "browserName": browser_name,
        "browserVersion": "latest",
        "platformName": platform,
        "sauce:options": sauce_options,
    }
    import json
    from urllib.parse import quote
    cdp_url = (
        f"wss://{host}/playwright?caps={quote(json.dumps(capabilities['sauce:options']))}"
        f"&browserName={browser_name}&browserVersion=latest"
    )
    browser = playwright.chromium.connect(cdp_url)
    context = browser.new_context()
    pagina = context.new_page()
    yield pagina
    context.close()
    browser.close()


@pytest.fixture
def actor(request, base_url) -> Actor:
    """Un actor llamado Ana que navega con el navegador adecuado.

    - Si SAUCE=1 y hay credenciales -> usa el navegador REAL en Sauce (page_sauce).
    - En caso contrario -> usa el navegador LOCAL de pytest-playwright (page).

    El resto del framework (tasks, questions, features) es identico en ambos casos.
    """
    if _usar_sauce():
        pagina = request.getfixturevalue("page_sauce")
    else:
        pagina = request.getfixturevalue("page")
    return Actor.llamado("Ana").que_puede(
        NavegarConElNavegador.usando(pagina, base_url)
    )
