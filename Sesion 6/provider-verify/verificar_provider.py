"""
VERIFICACION DEL PROVIDER (lado provider de Pact).

Toma el contrato que genero el CONSUMER (pacts/notificaciones-tienda-api.json)
y lo verifica contra el PROVIDER REAL corriendo. Es decir:
  - Lee cada interaccion del contrato (ej. GET /api/productos/1 -> 200 con id,
    nombre, precio...).
  - Hace esa peticion REAL al provider.
  - Comprueba que la respuesta del provider CUMPLE lo que el consumer espera
    (status y FORMA del cuerpo, por tipos).

Si el provider cambiara su respuesta (ej. renombrara 'precio' a 'valor'), esta
verificacion FALLARIA: eso es contract testing atrapando una ruptura ANTES de
que llegue a produccion y rompa al consumer.

Variables de entorno:
  PROVIDER_URL   -> URL base del provider (ej. http://provider-tienda:3000)
  PACT_FILE      -> ruta al contrato (ej. /pacts/notificaciones-tienda-api.json)
"""
import os
import sys

from pact import Verifier

PROVIDER_URL = os.environ.get("PROVIDER_URL", "http://localhost:3000")
PACT_FILE = os.environ.get("PACT_FILE", "../pacts/notificaciones-tienda-api.json")


def main():
    print(f"Verificando el provider en {PROVIDER_URL}")
    print(f"Contra el contrato {PACT_FILE}")

    verifier = Verifier(
        provider="tienda-api",
        provider_base_url=PROVIDER_URL,
    )

    # provider_states_setup_url: endpoint que Pact llama antes de cada interaccion
    # para poner al provider en el estado declarado (ej. "existe el producto 1").
    exito, _ = verifier.verify_pacts(
        PACT_FILE,
        provider_states_setup_url=f"{PROVIDER_URL}/api/_pact/state",
    )

    if exito == 0:
        print("\nOK — el provider CUMPLE el contrato del consumer.")
        sys.exit(0)
    else:
        print("\nFALLO — el provider NO cumple el contrato. Revisa los cambios de la API.")
        sys.exit(1)


if __name__ == "__main__":
    main()
