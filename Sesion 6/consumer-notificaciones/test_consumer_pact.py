"""
TEST DEL CONSUMER (lado consumer de Pact).

Que hace este test:
  1. Levanta un "mock provider" (un servidor falso que Pact controla).
  2. Declara el CONTRATO: "cuando pida GET /api/productos/1, espero un 200 con
     un cuerpo que tenga id, nombre (texto), precio (numero)...".
  3. Corre nuestro ClienteProductos contra ese mock.
  4. Si el cliente funciona con esa respuesta, Pact ESCRIBE el contrato en
     ../pacts/notificaciones-tienda.json

OJO: aqui NO se toca el provider real. Esto corre solo con el mock de Pact.
El provider se verifica DESPUES, con test_provider_verify (lado provider).

Como correr:
    pip install -r requirements.txt
    pytest -v
"""
import atexit
import os

import pytest
from pact import Consumer, Provider, Like

from cliente_productos import ClienteProductos

# Pact levanta un mock provider en este host/puerto. El cliente apuntara aqui.
PACT_MOCK_HOST = "localhost"
PACT_MOCK_PORT = 1234

# Donde se escribe el contrato. En contenedor usamos /pacts (volumen compartido
# con la verificacion del provider); en local, ../pacts. Configurable por env.
PACT_DIR = os.environ.get("PACT_DIR", "../pacts")

# Define el par consumer<->provider y donde se escribe el contrato (pact file).
pact = Consumer("notificaciones").has_pact_with(
    Provider("tienda-api"),
    host_name=PACT_MOCK_HOST,
    port=PACT_MOCK_PORT,
    pact_dir=PACT_DIR,
)

pact.start_service()
atexit.register(pact.stop_service)


@pytest.fixture
def cliente():
    return ClienteProductos(f"http://{PACT_MOCK_HOST}:{PACT_MOCK_PORT}")


def test_obtener_producto_existente(cliente):
    # La FORMA esperada del producto (Pact valida tipos, no valores exactos).
    cuerpo_esperado = {
        "id": Like(1),
        "nombre": Like("Tasty Concrete Chair"),
        "categoria": Like("hogar"),
        "precio": Like(106.25),
        "stock": Like(5),
    }

    (
        pact
        .given("existe el producto 1")                  # provider state
        .upon_receiving("una peticion del producto 1")  # descripcion
        .with_request("get", "/api/productos/1")         # lo que el consumer pide
        .will_respond_with(200, body=cuerpo_esperado)    # lo que el consumer espera
    )

    with pact:
        # Corremos el cliente REAL contra el mock. Si pasa, el contrato es valido.
        resumen = cliente.resumen_para_notificar(1)
        assert "Producto" in resumen
        assert "$" in resumen
